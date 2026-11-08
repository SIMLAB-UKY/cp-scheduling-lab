# Phase 6 — Verification and Benchmarking

## Goal

Compare **monolithic IBM CP Optimizer** with **lot-based CP large-neighborhood search (LNS)** on the same synthetic 30-lot, 90-operation, five-tool scheduling instance. Report reproducible schedules, **end-to-end wall-clock runtime**, and independent feasibility checks. Lower combined objective is better: `(horizon + 1) * weighted_tardiness + makespan`. On `benchmark_30.dat`, `horizon = 350` and the factor is 351.

## Requirements

- Windows, Python 3.10+ and IBM CPLEX Optimization Studio 22.2 (`oplrun.exe`)
- Existing project files in `../05_decomposition/01_monolithic` and `../05_decomposition/02_lot_decomposition`
- No third-party Python packages required

## Files

- `benchmark.py` — runs both methods at each specified nominal budget, records full process wall-clock time, independently verifies outputs with Phase 5A's `verify_schedule.py`, and produces CSV/JSON/Markdown reports.
- `test_benchmark.py` — unit tests for log parsing, UTF-16 decoding, objective consistency, run-limit model copies, and report generation.

The runner **does not edit** your original Phase 5A model. It creates a temporary copy with the requested CP TimeLimit and Workers. The LNS method uses its existing Phase 5B implementation and accepts only verified improvements.

## Run in VS Code PowerShell

From the repository root:

```powershell
cd .\06_verification_benchmarking
python .\test_benchmark.py
python .\benchmark.py --budgets 5 30 --trials 1
```

If `oplrun.exe` cannot be found, supply the exact path:

```powershell
python .\benchmark.py --opl "C:\Program Files\IBM\ILOG\CPLEX_Studio222\opl\bin\x64_win64\oplrun.exe" --budgets 5 30 --trials 1
```

For more robust comparisons, use three independent executions per setting (CP parallel search can vary):

```powershell
python .\benchmark.py --budgets 5 30 --trials 3
```

For a longer LNS exploration, the default `--max-subproblems 30` avoids prematurely stopping after six subproblems. Adjust `--batch-size`, `--subproblem-seconds`, and `--max-subproblems` as needed, but record their values when reporting results.

## Outputs

The `results/` directory (ignored by Git) contains:

- `results.csv`: machine-readable summary for all completed runs
- `results.json`: identical summary plus horizon
- `results.md`: ready-to-paste benchmark table
- One OPL/LNS solution log per run
- LNS orchestration console logs

A row is labeled `PASS` **only if the original independent verifier accepts the full solution** and the reported objective matches the computed objective. Any failed run remains in the table with an error status, not invented zero results.

## Previously observed Phase 5 results

These were reported from the earlier user-run experiments, **not executed by this Phase 6 package**:

| Method | Weighted tardiness | Makespan | Objective | Measured time | Verification |
|---|---:|---:|---:|---|---|
| Monolithic CP, 5-second solver limit | 1,363 | 151 | 478,564 | 5.01s *solver time* | PASS |
| LNS, nominal 5-second budget | 1,778 | 173 | 624,251 | 3.24s *elapsed* | Internal PASS; independent verification still pending |
| LNS, nominal 30-second budget | 1,715 | 159 | 602,124 | 14.26s *elapsed* | Independent PASS |

Monolithic CP has the best observed objective. The timings above are **not directly equivalent**, because the monolithic measurement excludes process startup and generation. The new runner measures all methods using the same wall-clock timing mechanism. CP and LNS budgets are nominal controls; report actual elapsed time. The experiment is a single synthetic instance, not evidence of general algorithmic superiority.

## Verification criteria

Every run must satisfy: 90 operations exactly once; tool eligibility; processing duration; lot release time; operation precedence; tool non-overlap; maintenance windows; lot completion reporting; and objective recomputation. These are checked through the existing Phase 5 verifier.

## Interpretation

This Phase 6 benchmark is a **methods-and-engineering portfolio project**, not proof that decomposition wins. The initial lot-based LNS improved its greedy seed but did not beat monolithic CP. Repeating on more random seeds/instances, experimenting with monolithic-initialized LNS, and trying larger neighborhoods are appropriate *future work*.
