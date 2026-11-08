"""Run reproducible monolithic CP and lot-based LNS comparisons.

Requires IBM oplrun and the sibling Phase 5A/5B project folders.
Each run is independently verified before its metrics are included in reports.
All wall times include process startup, model generation, solving, and output.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MONO = ROOT / '05_decomposition' / '01_monolithic'
DECOMP = ROOT / '05_decomposition' / '02_lot_decomposition'


def parse_log(content: str, horizon: int) -> dict:
    """Extract and cross-check the objective reported in a verified solution log."""
    summaries = re.findall(r'^SUMMARY\s*,\s*(\d+)\s*,\s*(\d+)\s*$', content, re.M)
    if len(summaries) != 1:
        raise ValueError(f'Expected exactly one SUMMARY record, found {len(summaries)}')
    wt, ms = map(int, summaries[0])
    if ms > horizon:
        raise ValueError('Makespan exceeds benchmark horizon')
    objective = (horizon + 1) * wt + ms
    match = re.search(r'^OBJECTIVE:\s*(\d+)\s*$', content, re.M)
    if match and int(match.group(1)) != objective:
        raise ValueError('Reported objective disagrees with independently calculated objective')
    return {'weighted_tardiness': wt, 'makespan': ms, 'objective': objective}


def read_horizon(data_file: Path) -> int:
    match = re.search(r'\bhorizon\s*=\s*(\d+)\s*;', data_file.read_text(encoding='utf-8-sig'))
    if not match:
        raise ValueError('No horizon found in benchmark .dat')
    return int(match.group(1))


def decode_process_output(data: bytes) -> str:
    if data.startswith((b'\xff\xfe', b'\xfe\xff')):
        return data.decode('utf-16')
    if b'\x00' in data[:100]:
        return data.decode('utf-16-le')
    return data.decode('utf-8-sig', errors='replace')


def verify(log: Path, data: Path, verifier: Path) -> tuple[bool, str]:
    check = subprocess.run([sys.executable, str(verifier), '--data', str(data), '--log', str(log)],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = decode_process_output(check.stdout + check.stderr).strip()
    return check.returncode == 0 and 'PASS:' in output, output


def find_opl(path: str | None) -> Path:
    options = [path, shutil.which('oplrun'),
               r'C:\Program Files\IBM\ILOG\CPLEX_Studio222\opl\bin\x64_win64\oplrun.exe']
    for candidate in options:
        if candidate and Path(candidate).is_file():
            return Path(candidate).resolve()
    raise FileNotFoundError('Cannot find oplrun.exe. Supply --opl with its full Windows path.')


def make_limited_model(original: Path, dest: Path, seconds: int, workers: int) -> None:
    """Create a temporary copy with the requested CP limit, preserving the original model."""
    src = original.read_text(encoding='utf-8-sig')
    # Replace the single parameter block used in Phase 5A; do not alter objective/constraints.
    time_pattern = r'cp\.param\.TimeLimit\s*=\s*\d+\s*;'
    workers_pattern = r'cp\.param\.Workers\s*=\s*\d+\s*;'
    if len(re.findall(time_pattern, src)) != 1 or len(re.findall(workers_pattern, src)) != 1:
        raise ValueError('Expected exactly one CP TimeLimit and Workers parameter in monolithic.mod')
    src = re.sub(time_pattern, f'cp.param.TimeLimit = {seconds};', src)
    src = re.sub(workers_pattern, f'cp.param.Workers = {workers};', src)
    dest.write_text(src, encoding='utf-8')


def run_one(method: str, budget: int, trial: int, args, out: Path, horizon: int, opl: Path | None) -> dict:
    name = f'{method}_{budget}s_run{trial}'
    log = out / f'{name}.log'
    row = {'method': method, 'budget_seconds': budget, 'trial': trial,
           'actual_wall_seconds': '', 'weighted_tardiness': '', 'makespan': '',
           'objective': '', 'verified': False, 'status': '', 'log': str(log.relative_to(out))}
    with tempfile.TemporaryDirectory(prefix='cp_bench_') as tmp:
        if method == 'monolithic':
            assert opl is not None
            model = Path(tmp) / 'monolithic.mod'
            make_limited_model(MONO / 'monolithic.mod', model, budget, args.workers)
            cmd = [str(opl), str(model), str(args.data)]
        else:
            cmd = [sys.executable, str(DECOMP / 'run_decomposition.py'),
                   '--data', str(args.data), '--budget', str(budget),
                   '--batch-size', str(args.batch_size),
                   '--subproblem-seconds', str(min(args.subproblem_seconds, budget)),
                   '--max-subproblems', str(args.max_subproblems),
                   '--workers', str(args.workers), '--output', str(log)]
            if args.opl:
                cmd.extend(['--opl', args.opl])
        start = time.perf_counter()
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  timeout=budget + args.grace_seconds)
            row['actual_wall_seconds'] = round(time.perf_counter() - start, 3)
            stdout = decode_process_output(proc.stdout)
            stderr = decode_process_output(proc.stderr)
            if method == 'monolithic':
                log.write_text(stdout + ('\nSTDERR:\n' + stderr if stderr else ''), encoding='utf-8')
            else:
                (out / f'{name}.console.txt').write_text(stdout + '\n' + stderr, encoding='utf-8')
            if proc.returncode != 0:
                raise RuntimeError(f'Process exit code {proc.returncode}: {(stderr or stdout)[-400:]}')
            if not log.is_file():
                raise RuntimeError('Solver did not create a log')
            success, output = verify(log, args.data, MONO / 'verify_schedule.py')
            if not success:
                raise RuntimeError(f'Independent verification failed: {output[-400:]}')
            row.update(parse_log(log.read_text(encoding='utf-8-sig'), horizon))
            row['verified'] = True
            row['status'] = 'PASS'
        except (subprocess.TimeoutExpired, RuntimeError, ValueError, OSError) as exc:
            row['status'] = f'ERROR: {str(exc)[:200]}'
            if not row['actual_wall_seconds']:
                row['actual_wall_seconds'] = round(time.perf_counter() - start, 3)
    return row


def write_reports(rows: list[dict], output: Path, horizon: int) -> None:
    columns = ['method','budget_seconds','trial','actual_wall_seconds','weighted_tardiness',
               'makespan','objective','verified','status','log']
    with (output / 'results.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    (output / 'results.json').write_text(json.dumps({'horizon': horizon, 'runs': rows}, indent=2), encoding='utf-8')
    lines = ['# Phase 6 benchmark results', '',
             'All durations are measured **end-to-end wall-clock seconds** by Python. '
             'The CP solver TimeLimit and LNS budget are nominal controls, not equal-runtime guarantees.', '',
             '| Method | Budget | Trial | Wall time (s) | Weighted tardiness | Makespan | Objective | Verified |',
             '|---|---:|---:|---:|---:|---:|---:|---|']
    for r in rows:
        lines.append(f"| {r['method']} | {r['budget_seconds']} | {r['trial']} | "
                     f"{r['actual_wall_seconds']} | {r['weighted_tardiness']} | {r['makespan']} | "
                     f"{r['objective']} | {r['status']} |")
    lines += ['', 'Lower weighted tardiness is preferable; makespan is a secondary tie-breaker.',
              'Only independently verified runs should be used for performance conclusions.',
              'These results apply to one synthetic instance; they do not establish general superiority.']
    (output / 'results.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, default=MONO / 'benchmark_30.dat')
    p.add_argument('--output-dir', type=Path, default=HERE / 'results')
    p.add_argument('--budgets', type=int, nargs='+', default=[5, 30])
    p.add_argument('--trials', type=int, default=1)
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--batch-size', type=int, default=10)
    p.add_argument('--subproblem-seconds', type=int, default=5)
    p.add_argument('--max-subproblems', type=int, default=30)
    p.add_argument('--grace-seconds', type=int, default=15)
    p.add_argument('--opl', help='Full path to oplrun.exe')
    args = p.parse_args()
    if args.trials < 1 or min(args.budgets) < 1 or args.workers < 1:
        p.error('trials, budgets, and workers must be positive')
    args.data = args.data.resolve()
    if not args.data.is_file():
        p.error(f'Data file not found: {args.data}')
    for required in (MONO / 'monolithic.mod', MONO / 'verify_schedule.py',
                     DECOMP / 'run_decomposition.py', DECOMP / 'subproblem.mod'):
        if not required.is_file():
            p.error(f'Missing Phase 5 file: {required}')
    opl = find_opl(args.opl)
    horizon = read_horizon(args.data)
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for budget in args.budgets:
        for trial in range(1, args.trials + 1):
            for method in ('monolithic','decomposition'):
                print(f'Running {method} / {budget}s / trial {trial}', flush=True)
                row = run_one(method, budget, trial, args, out, horizon, opl)
                rows.append(row)
                write_reports(rows, out, horizon)
                print(f"  {row['status']} objective={row['objective']} elapsed={row['actual_wall_seconds']}s", flush=True)
    print(f'Reports: {out / "results.md"}')
    if any(not row['verified'] for row in rows):
        sys.exit(1)


if __name__ == '__main__':
    main()
