"""Reproducible lot-neighborhood CP scheduling with a validated greedy seed.

Runs IBM OPL subproblems on selected lots while fixing all other tool intervals.
Each accepted move preserves feasibility and strictly improves the global objective.
"""
from __future__ import annotations

import argparse
import math
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / "01_monolithic"


def parse_instance(path: Path):
    data = path.read_text(encoding="utf-8-sig")
    def num(name):
        m = re.search(rf"\b{name}\s*=\s*(\d+)\s*;", data)
        if not m:
            raise ValueError(f"Missing parameter {name}")
        return int(m.group(1))
    def arr(name):
        m = re.search(rf"\b{name}\s*=\s*\[([^\]]+)\]", data)
        if not m:
            raise ValueError(f"Missing array {name}")
        return [int(s) for s in re.findall(r"\d+", m.group(1))]
    def tuples(name, size):
        match = re.search(rf"\b{name}\s*=\s*\{{(.*?)\}}\s*;", data, re.S)
        if not match:
            raise ValueError(f"Missing tuple set {name}")
        pattern = r"<\s*" + r"\s*,\s*".join([r"(\d+)"] * size) + r"\s*>"
        return [tuple(map(int, x)) for x in re.findall(pattern, match.group(1))]
    ins = dict(nLots=num("nLots"), nOps=num("nOps"), nTools=num("nTools"),
               horizon=num("horizon"), release=arr("release"), due=arr("due"),
               weight=arr("weight"), choices=tuples("choices", 4),
               maintenance=tuples("maintenance", 3))
    if not all(len(ins[key]) == ins["nLots"] for key in ("release", "due", "weight")):
        raise ValueError("Lot-array lengths do not match nLots")
    return ins


def score(ins, schedule):
    completion = {j: schedule[j, ins["nOps"]][2] for j in range(1, ins["nLots"] + 1)}
    wt = sum(ins["weight"][j-1] * max(0, completion[j] - ins["due"][j-1])
             for j in completion)
    ms = max(completion.values())
    return (ins["horizon"] + 1) * wt + ms, wt, ms


def assert_feasible(ins, schedule):
    eligible = {(j,o,m): p for j,o,m,p in ins["choices"]}
    required = {(j,o) for j in range(1,ins["nLots"]+1) for o in range(1,ins["nOps"]+1)}
    if set(schedule) != required:
        raise ValueError(f"Missing/extra operations: {required ^ set(schedule)}")
    blocks = defaultdict(list)
    for m,s,e in ins["maintenance"]:
        blocks[m].append((s,e,"maintenance"))
    for (j,o),(m,s,e) in schedule.items():
        if (j,o,m) not in eligible or e-s != eligible[j,o,m]:
            raise ValueError(f"Invalid tool or duration for {(j,o)}")
        if s < ins["release"][j-1] or s < 0 or e > ins["horizon"]:
            raise ValueError(f"Invalid time window for {(j,o)}")
        if o > 1 and schedule[j,o-1][2] > s:
            raise ValueError(f"Precedence violation at {(j,o)}")
        blocks[m].append((s,e,f"{j}-{o}"))
    for m, spans in blocks.items():
        spans.sort()
        for a,b in zip(spans,spans[1:]):
            if a[1] > b[0]:
                raise ValueError(f"Tool {m} overlap {a}, {b}")


def greedy_initial(ins):
    """Earliest-finish insertion heuristic, scheduling lots by weighted due-date urgency."""
    possible = defaultdict(list)
    for j,o,m,p in ins["choices"]:
        possible[j,o].append((m,p))
    busy = defaultdict(list)
    for m,s,e in ins["maintenance"]:
        busy[m].append((s,e))
    schedule = {}
    lots = list(range(1,ins["nLots"]+1))
    lots.sort(key=lambda j: (ins["due"][j-1] / ins["weight"][j-1],
                             ins["due"][j-1], ins["release"][j-1], j))
    for j in lots:
        ready = ins["release"][j-1]
        for o in range(1,ins["nOps"]+1):
            candidates = []
            for m,p in possible[j,o]:
                start = ready
                for bs,be in sorted(busy[m]):
                    if start + p <= bs:
                        break
                    if start < be and start + p > bs:
                        start = be
                candidates.append((start + p, start, m, p))
            if not candidates:
                raise ValueError(f"No eligible tool for lot {j}, operation {o}")
            end,start,m,p = min(candidates)
            if end > ins["horizon"]:
                raise ValueError("Greedy schedule exceeds horizon; enlarge instance horizon")
            schedule[j,o] = (m,start,end)
            busy[m].append((start,end))
            ready = end
    assert_feasible(ins,schedule)
    return schedule


def as_dat(ins, subset, fixed, seconds, workers):
    mapped = {j:i for i,j in enumerate(sorted(subset), 1)}
    selected = sorted(subset)
    choices = [(mapped[j],o,m,p) for j,o,m,p in ins["choices"] if j in mapped]
    blocked = list(ins["maintenance"])
    blocked.extend((m,s,e) for (j,o),(m,s,e) in fixed.items() if j not in mapped)
    def tup_lines(rows):
        return "{\n" + ",\n".join("  <" + ",".join(map(str,row)) + ">" for row in rows) + "\n}"
    lines = [f"nLots = {len(selected)};", f"nOps = {ins['nOps']};",
             f"nTools = {ins['nTools']};", f"horizon = {ins['horizon']};",
             f"timeLimit = {seconds};", f"workers = {workers};"]
    for key in ("release", "due", "weight"):
        lines.append(key + " = [" + ", ".join(str(ins[key][j-1]) for j in selected) + "];")
    lines += ["choices = " + tup_lines(choices) + ";",
              "blocked = " + tup_lines(blocked) + ";"]
    return "\n".join(lines)+"\n", {v:k for k,v in mapped.items()}


def parse_local_output(output, index_to_global, n_ops):
    results = {}
    summary_found = False
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("LOCAL_SUMMARY,"):
            summary_found = True
        if line.startswith("LOCAL_ASSIGN,"):
            parts = line.split(",")
            if len(parts) != 6:
                raise ValueError(f"Malformed CP output: {line}")
            _,j,o,m,s,e = parts
            key = (index_to_global[int(j)], int(o))
            if key in results:
                raise ValueError(f"Duplicate CP assignment {key}")
            results[key] = (int(m),int(s),int(e))
    if not summary_found or len(results) != len(index_to_global)*n_ops:
        raise ValueError("Subproblem did not return a complete solution")
    return results


def solve_subset(opl, model, ins, subset, schedule, sec, workers, directory):
    dat, mapping = as_dat(ins, subset, schedule, sec, workers)
    path = directory / "subproblem.dat"
    path.write_text(dat, encoding="utf-8")
    try:
        p = subprocess.run([str(opl), str(model), str(path)], capture_output=True,
                           text=True, encoding="utf-8", errors="replace",
                           timeout=sec+3, check=False)
    except subprocess.TimeoutExpired:
        print(f"CP timeout for {len(subset)} lots; retaining prior schedule", flush=True)
        return None
    if p.returncode:
        print(f"CP exit code {p.returncode}: {(p.stdout+p.stderr)[-1200:]}", flush=True)
        return None
    try:
        return parse_local_output(p.stdout, mapping, ins["nOps"])
    except ValueError as ex:
        print(f"No complete CP solution: {ex}. Retaining prior schedule.", flush=True)
        return None


def write_log(path, ins, schedule, history):
    obj,wt,ms = score(ins,schedule)
    with path.open("w",encoding="utf-8") as f:
        f.write("PHASE5B LOT-BASED CP DECOMPOSITION\n")
        for message in history:
            f.write("INFO,"+message+"\n")
        f.write(f"OBJECTIVE: {obj}\nSUMMARY,{wt},{ms}\n")
        for j in range(1,ins["nLots"]+1):
            f.write(f"LOT,{j},{ins['release'][j-1]},{ins['due'][j-1]},{ins['weight'][j-1]},{schedule[j,ins['nOps']][2]}\n")
        for (j,o),(m,s,e) in sorted(schedule.items()):
            f.write(f"ASSIGN,{j},{o},{m},{s},{e}\n")
    return obj,wt,ms


def find_opl(explicit):
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            raise FileNotFoundError(f"No oplrun at {p}")
        return p
    exe = shutil.which("oplrun")
    if exe:
        return Path(exe)
    common = Path(r"C:\Program Files\IBM\ILOG\CPLEX_Studio222\opl\bin\x64_win64\oplrun.exe")
    return common if common.is_file() else None


def neighborhoods(ins, schedule, batch_size):
    lots = list(range(1,ins["nLots"]+1))
    # First pass: priority-weighted due-date windows, overlapping for flexibility.
    lots.sort(key=lambda j: (ins["due"][j-1], -ins["weight"][j-1], j))
    blocks = [lots[k:k+batch_size] for k in range(0,len(lots),batch_size)]
    # Later neighborhoods target expensive late lots together with their due-date neighbors.
    late = sorted(lots, key=lambda j: (
        -ins["weight"][j-1] * max(0,schedule[j,ins["nOps"]][2]-ins["due"][j-1]), j))
    if len(lots) > batch_size:
        top = late[:max(1,batch_size//2)]
        rest = [j for j in lots if j not in top]
        blocks.append(top + rest[:batch_size-len(top)])
        blocks.append(top + rest[-(batch_size-len(top)):])
    return [set(b) for b in blocks if b]


def run(args):
    ins = parse_instance(args.data)
    schedule = greedy_initial(ins)
    history = []
    obj,wt,ms = score(ins,schedule)
    print(f"Greedy seed: objective={obj}, tardiness={wt}, makespan={ms}",flush=True)
    history.append(f"GREEDY,{obj},{wt},{ms}")
    start = time.monotonic()
    opl = find_opl(args.opl)
    if not args.no_cp and opl is None:
        raise FileNotFoundError("oplrun not found; provide --opl or use --no-cp for greedy-only validation")
    model = ROOT/"subproblem.mod"
    attempts = 0
    accepted = 0
    if not args.no_cp:
        with tempfile.TemporaryDirectory(prefix="cp_lot_") as tmp:
            while time.monotonic()-start < args.budget - 0.4:
                if attempts >= args.max_subproblems:
                    break
                blocks = neighborhoods(ins,schedule,args.batch_size)
                subset = blocks[attempts % len(blocks)]
                remaining = args.budget-(time.monotonic()-start)
                if remaining < 1.3:
                    break
                sec = max(1, min(args.subproblem_seconds, math.floor(remaining-0.3)))
                attempts += 1
                t0 = time.monotonic()
                candidate = solve_subset(opl,model,ins,subset,schedule,sec,args.workers,Path(tmp))
                if candidate:
                    merged = {key:val for key,val in schedule.items() if key[0] not in subset}
                    merged.update(candidate)
                    try:
                        assert_feasible(ins,merged)
                        new_obj,new_wt,new_ms = score(ins,merged)
                        if new_obj < obj:
                            schedule = merged
                            obj,wt,ms = new_obj,new_wt,new_ms
                            accepted += 1
                            status = "ACCEPT"
                        else:
                            status = "REJECT"
                    except ValueError as exc:
                        status = "INVALID"
                        print(f"Rejected invalid subproblem: {exc}",flush=True)
                else:
                    status = "NO_SOLUTION"
                dt=time.monotonic()-t0
                message=f"STEP,{attempts},{status},size={len(subset)},seconds={dt:.2f},objective={obj}"
                print(message,flush=True)
                history.append(message)
    elapsed=time.monotonic()-start
    assert_feasible(ins,schedule)
    obj,wt,ms=write_log(args.output,ins,schedule,history)
    print(f"PASS internal validation: {len(schedule)} operations, {ins['nTools']} tools",flush=True)
    print(f"FINAL: objective={obj}; weighted tardiness={wt}; makespan={ms}",flush=True)
    print(f"Elapsed={elapsed:.2f}s; subproblems={attempts}; accepted={accepted}",flush=True)
    print(f"Schedule: {args.output}",flush=True)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data",type=Path,default=BASE/"benchmark_30.dat")
    parser.add_argument("--output",type=Path,default=ROOT/"decomposed.log")
    parser.add_argument("--opl",help="Full path to oplrun.exe (defaults to PATH or CPLEX 22.2)")
    parser.add_argument("--budget",type=float,default=30,help="Approximate total wall-clock budget, seconds")
    parser.add_argument("--batch-size",type=int,default=10)
    parser.add_argument("--subproblem-seconds",type=int,default=5)
    parser.add_argument("--max-subproblems",type=int,default=6)
    parser.add_argument("--workers",type=int,default=4)
    parser.add_argument("--no-cp",action="store_true",help="Validate greedy seed without invoking IBM CP")
    a=parser.parse_args()
    if a.batch_size < 1 or a.budget <= 0 or a.subproblem_seconds < 1:
        parser.error("batch-size, budget and subproblem-seconds must be positive")
    run(a)
