# Phase 5A — Monolithic CP baseline (30 wafer lots)

A reproducible, synthetic scheduling benchmark for comparing monolithic CP with future decomposition approaches. This is **not** an Intel dataset.

## Data and decisions

- 30 lots, three sequential operations per lot, five tools.
- Eligibility: step 1 → tools 1 or 3; step 2 → tools 2, 4 or 5; step 3 → tools 1, 3 or 5 (reentrant tool families).
- Lot release times, priority weights, and deliberately tight due dates.
- Fixed downtime: tool 2 from time 30 to 43; tool 4 from time 75 to 90.
- Tool-dependent processing times; non-preemptive operations.

The objective is `351 × total weighted tardiness + makespan`. Because the makespan is bounded by 350 and weights/tardiness are integers, this optimizes weighted tardiness first and makespan second. A 30-second **elapsed** CP search cap and 4 workers are set in the model; a feasible solution returned by the solver is not necessarily proven optimal. Record **objective, best bound, status, solve time** for benchmarking.

## Files

- `generate_instance.py`: reproducible generator (`random.Random(20261106)`)
- `benchmark_30.dat`: generated fixture, committed so others can run the exact same data
- `monolithic.mod`: CP Optimizer / OPL model
- `verify_schedule.py`: independent checking of lot release, processing duration, eligibility, precedence, maintenance, no-overlap, and reported objective components

## Run on Windows PowerShell from this folder

```powershell
python .\generate_instance.py
$opl = "C:\Program Files\IBM\ILOG\CPLEX_Studio222\opl\bin\x64_win64\oplrun.exe"
& $opl .\monolithic.mod .\benchmark_30.dat | Tee-Object -FilePath .\run_30.log
python .\verify_schedule.py --log .\run_30.log
```

Use `*.log` in `.gitignore` (and check for confidential/private inputs before publishing).

## Acceptance criteria

1. Model compiles with the installed OPL 22.2 runner.
2. Solver returns a feasible schedule and reports summary/assignment lines.
3. The independent verifier prints `PASS` for 90 operations, with zero tool conflicts or maintenance overlaps.
4. Record feasible objective, best bound, gap, and solve time. Distinguish feasible from proven optimal.
5. Commit the `.mod`, `.dat`, generator, verifier, README; do not commit the solver log unless intentionally wanted.

## Benchmark extension

Next, solve the same fixture using a decomposition method (e.g. lot-based partitions with a coordination step). Compare on *the same input and time budget*: feasibility, weighted tardiness, makespan, bound/optimality, runtime, and independent verification.
