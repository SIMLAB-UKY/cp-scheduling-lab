## Phase 6 — Independent Verification and Benchmarking

**Status: Completed**

Phase 6 provides an automated and reproducible benchmarking framework comparing monolithic constraint programming against lot-based CP decomposition.

### Benchmark Setup

- 30 wafer lots
- 90 processing operations
- 5 manufacturing tools
- IBM ILOG CP Optimizer 22.2
- Nominal computational budgets of 5 and 30 seconds
- End-to-end wall-clock runtime measurement
- Independent schedule verification

### Final Results

| Method | Budget | Wall Time (s) | Weighted Tardiness | Makespan | Combined Objective | Verification |
|---|---:|---:|---:|---:|---:|---|
| Monolithic CP | 5s | 5.049 | 1,363 | 151 | 478,564 | PASS |
| Lot Decomposition | 5s | 4.138 | 2,012 | 199 | 706,411 | PASS |
| Monolithic CP | 30s | 30.042 | 1,339 | 151 | **470,140** | PASS |
| Lot Decomposition | 30s | 29.577 | 1,620 | 158 | 568,778 | PASS |

### Key Findings

1. Monolithic CP produced the best solutions at both computational budgets.
2. Increasing the monolithic search budget from 5 to 30 seconds reduced its objective from 478,564 to 470,140.
3. Lot-based decomposition successfully generated feasible schedules, but fixing operations outside each neighborhood restricted its ability to improve the global schedule.
4. All four final schedules passed independent verification.
5. The benchmark framework successfully measured end-to-end wall-clock runtime and generated automated reports.

### Verification

The framework verifies:

- Operation completeness and uniqueness
- Tool eligibility
- Processing durations
- Operation precedence
- Release times
- Machine capacity constraints
- Maintenance restrictions
- Weighted tardiness
- Makespan
- Combined objective consistency

Six automated Python unit tests passed.

### Reproduce the Benchmark

From `06_verification_benchmarking/`:

```powershell
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

## Git commit

From the repository root:

```powershell
git add 06_verification_benchmarking/
git commit -m "Add Phase 6 CP scheduling benchmark and verification runner"
git push
```

Keep the `results/` folder out of Git until reviewing it. Instead, copy verified summary metrics from `results.md` into this README or a separate curated `BENCHMARK_RESULTS.md`.
