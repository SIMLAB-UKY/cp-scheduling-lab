# Phase 5B — Lot-based CP decomposition

**Status:** Python construction and independent verification tested; IBM CP Optimizer subproblem execution must be run locally with OPL 22.2.

## Purpose

Optimize **the exact same 30-lot, 90-operation, five-tool fixture** used in Phase 5A, using a schedule-construction step and repeated CP neighborhood subproblems. The method is *lot-based large-neighborhood search (LNS)*, **not Benders, Dantzig–Wolfe, or Lagrangian decomposition**, and it does not certify global optimality.

The procedure first builds a deterministic earliest-finish insertion schedule, processing more urgent lots first. For each CP neighborhood, a subset of lots is released for reoptimization; every operation belonging to the other lots is copied into an immutable tool-blocking interval alongside the original maintenance windows. CP Optimizer reschedules only the selected lots. The merged schedule is checked in Python for eligibility, durations, releases, precedence, machine overlap, and maintenance conflicts. A candidate is accepted only if its **global** objective improves.

The objective is exactly the monolithic objective: `351 * weighted_tardiness + makespan`. Lower is better.

## Files

- `subproblem.mod` — CP Optimizer OPL model for selected lots and fixed tool reservations.
- `run_decomposition.py` — instance parser, deterministic feasible seed, CP-subproblem generation, orchestration, acceptance, and UTF-8 result log.
- `test_decomposition.py` — unit checks for instance parsing, schedule validation, data generation, and solver record parsing.
- `README.md` — method, commands, validation, limitations.

Read the unchanged benchmark file from `../01_monolithic/benchmark_30.dat`. The independent verifier from Phase 5A checks `decomposed.log` directly.

## Run from the `02_lot_decomposition` folder in Windows PowerShell

```powershell
# Quick test: independently verifiable greedy seed, no IBM solver needed
python .\run_decomposition.py --no-cp --output .\greedy.log
python ..\01_monolithic\verify_schedule.py --data ..\01_monolithic\benchmark_30.dat --log .\greedy.log

# CP decomposition with a nominal 30-second wall-clock budget
python .\run_decomposition.py --budget 30 --batch-size 10 --subproblem-seconds 5 --max-subproblems 6 --output .\decomposed_30s.log
python ..\01_monolithic\verify_schedule.py --data ..\01_monolithic\benchmark_30.dat --log .\decomposed_30s.log

# Compare at the 5-second setting of the earlier monolithic baseline
python .\run_decomposition.py --budget 5 --batch-size 10 --subproblem-seconds 1 --max-subproblems 3 --output .\decomposed_5s.log
python ..\01_monolithic\verify_schedule.py --data ..\01_monolithic\benchmark_30.dat --log .\decomposed_5s.log
```

The script searches PATH and then your known installation at `C:\Program Files\IBM\ILOG\CPLEX_Studio222\opl\bin\x64_win64\oplrun.exe`. If necessary, provide `--opl "C:\...\oplrun.exe"`.

Run the Python-only unit tests:

```powershell
python .\test_decomposition.py
```

## Baseline and results

Phase 5A: five-second monolithic search returned weighted tardiness **1,363**, makespan **151**, objective **478,564**, best bound **66**; the schedule passed independent validation. It was **not** proven optimal.

Phase 5B results should be recorded only after running the CP subproblems locally. In particular, **greedy-only is not a claim of CP decomposition improvement**. The Python-only baseline produced a feasible schedule with weighted tardiness **2,249**, makespan **199**, objective **789,598**; it is an initial point, not a benchmark winner.

| Method | End-to-end time | Weighted tardiness | Makespan | Combined objective | Independently verified? |
|---|---:|---:|---:|---:|---|
| Monolithic CP, 5s (observed) | 5.01s solve | 1363 | 151 | 478564 | Yes |
| Decomposed CP, 5s | Run locally | — | — | — | Pending |
| Monolithic CP, 30s | Run locally | — | — | — | Pending |
| Decomposed CP, 30s | Run locally | — | — | — | Pending |

**Fairness notes:** CP search limits do not account for OPL startup/generation/output, and the monolithic baseline reports solver time whereas this orchestrator reports end-to-end wall-clock time. For a strong comparison, time the complete monolithic `oplrun` command in PowerShell with `Measure-Command` as well. Due to concurrent CP workers, runs can vary. Repeat comparisons over multiple runs and preferably multiple synthetic instances.

## Limitations

- Fixing the other lots restricts the neighborhood; important improvements may require moving many lots simultaneously. Local optimality is not global optimality.
- A short CP time limit can produce no usable schedule; the script keeps the last validated schedule.
- The 30-second budget is an **approximate** wall-clock cap: a subproblem may require extra startup/cleanup time. Inspect the actual elapsed time printed by the script.
- No objective lower bound is provided by the decomposition controller. Do not interpret the monolithic CP bound as an LNS bound.
- This is a synthetic benchmark, not an Intel dataset or a deployable manufacturing control system.

## Repository milestone

Once local CP execution and verification pass:

```powershell
git add 05_decomposition/02_lot_decomposition/
git commit -m "Add validated lot-based CP decomposition baseline"
git push
```

Keep solver logs out of Git using `*.log` in `.gitignore` unless intentionally reporting a sanitized benchmark result.
