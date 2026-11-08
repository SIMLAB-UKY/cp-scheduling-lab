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

## Results and Benchmark Comparison

The decomposition algorithm was evaluated on the same synthetic semiconductor scheduling benchmark as the monolithic CP model.

### Benchmark Configuration

| Parameter | Value |
|---|---|
| Wafer lots | 30 |
| Operations per lot | 3 |
| Total operations | 90 |
| Processing tools | 5 |
| Optimization solver | IBM CP Optimizer 22.2 |
| Objective | Minimize weighted tardiness, then makespan |
| Decomposition method | Lot-based CP Large Neighborhood Search |
| Subproblem batch size | 10 lots |
| Independent verification | `verify_schedule.py` |

### Performance Comparison

| Method | Weighted Tardiness | Makespan | Combined Objective | Runtime | Verification |
|---|---:|---:|---:|---:|---|
| Monolithic CP (5s) | **1,363** | **151** | **478,564** | 5.01 s | PASS |
| Decomposition (5s budget) | 1,778 | 173 | 624,251 | 3.24 s | Internal PASS |
| Decomposition (30s budget) | 1,715 | 159 | 602,124 | 14.26 s | PASS |

**Note:** The monolithic runtime represents CP Optimizer solver time, while decomposition runtime includes orchestration. The results are preliminary and are not a strictly equal wall-clock comparison.

### Decomposition Search Progress

The decomposition algorithm started with a greedy feasible schedule and iteratively re-optimized selected groups of 10 lots.

| Metric | Initial Solution | 5s Budget | 30s Budget |
|---|---:|---:|---:|
| Combined objective | 789,598 | 624,251 | 602,124 |
| Weighted tardiness | 2,249 | 1,778 | 1,715 |
| Makespan | 199 | 173 | 159 |
| CP subproblems solved | 0 | 3 | 6 |
| Accepted improvements | — | 3 | 4 |
| Elapsed time | — | 3.24 s | 14.26 s |
| Objective reduction from initial solution | — | 20.9% | 23.7% |

### Key Findings

1. **The decomposition algorithm successfully improved the initial feasible schedule.** The combined objective decreased by 23.7% in the longer experiment.

2. **Monolithic CP outperformed the initial decomposition approach.** The monolithic model achieved a combined objective of 478,564, compared with 602,124 for the best decomposed schedule.

3. **Decomposition preserved feasibility.** The 30-second-budget schedule passed independent verification of all 90 operations, including processing times, tool eligibility, precedence constraints, release times, maintenance restrictions, and machine capacity.

4. **Fixing operations outside each neighborhood can limit solution quality.** Better solutions may require coordinated changes across multiple groups of lots.

5. **Increasing the allowed search budget did not proportionally increase runtime.** The 30-second-budget experiment ended after 14.26 seconds because the maximum number of six subproblems was reached.

### Limitations

- The experiment uses one synthetic 30-lot benchmark.
- The decomposition method begins from a greedy initial schedule.
- Neighborhoods contain 10 selected lots, with the remaining operations fixed.
- No global optimality guarantee is established for the decomposition algorithm.
- Computational budgets are not yet strictly comparable across methods.
- The five-second decomposition schedule passed internal checks but its independent verifier result has not yet been recorded.

### Next Improvements

- Initialize Large Neighborhood Search using a feasible monolithic CP solution.
- Explore different neighborhood sizes and lot-selection strategies.
- Compare methods under equal end-to-end wall-clock budgets.
- Evaluate multiple benchmark instances and random seeds.
- Record objective quality, solver bounds, runtime, and feasibility systematically.

### Conclusion

This experiment demonstrates a working CP-based decomposition framework for semiconductor scheduling.

Although the initial decomposition method did not outperform monolithic CP, it substantially improved its greedy starting solution while preserving schedule feasibility.

The main lesson is that **decomposition is not automatically superior to monolithic optimization**. Its effectiveness depends on the initial solution, neighborhood selection, coordination between subproblems, and computational budget.


