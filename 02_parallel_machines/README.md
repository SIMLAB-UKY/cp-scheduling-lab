# Phase 2 — Identical Parallel-Machine Scheduling

## 1. Problem Description

Five independent jobs must be scheduled on two identical parallel machines. Each job must be processed exactly once, on one machine, without interruption.

The optimizer decides:

- Which machine executes each job.
- When each job starts.
- The processing sequence on each machine.

## 2. Input Data

| Job | Processing Time |
|---|---:|
| J1 | 4 |
| J2 | 6 |
| J3 | 3 |
| J4 | 5 |
| J5 | 2 |

Number of machines: 2.

Total processing workload: 20 time units.

## 3. Mathematical Formulation

Let \(S_j\) be the start time, \(p_j\) the processing duration, and \(C_j\) the completion time of job \(j\).

\[
C_j = S_j + p_j
\]

The objective is:

\[
\min C_{\max} = \max_j C_j
\]

Subject to:

1. Every job is assigned to exactly one machine.
2. No two jobs assigned to the same machine overlap.
3. All jobs execute without interruption.

## 4. CP Optimizer Formulation

The implementation uses:

- `dvar interval` to represent each job.
- `optional` intervals for possible machine assignments.
- `alternative` to select exactly one machine per job.
- `noOverlap` to enforce exclusive machine capacity.
- `endOf` to calculate makespan.

Unlike a conventional MILP sequencing formulation, CP Optimizer handles machine conflicts directly through scheduling constraints.

## 5. Expected Optimal Result

The workload lower bound is:

\[
C_{\max} \geq \left\lceil \frac{20}{2} \right\rceil = 10
\]

One feasible schedule achieves this bound:

| Machine | Schedule | Completion |
|---|---|---:|
| M1 | J1 → J2 | 10 |
| M2 | J4 → J3 → J5 | 10 |

Therefore, the optimal makespan is **10 time units**.

This is an analytical benchmark; confirm the solver's reported objective and bound before marking the run verified.

## 6. Verification

Check that every job appears exactly once, its duration is correct, and no machine has overlapping jobs.

Compare the solver's objective against the analytical lower bound.

## 7. Run the Model

From the repository root:

```powershell
oplrun .\02_parallel_machines\parallel_machines.mod
```

## 8. Lessons Learned

This phase introduces machine-assignment decisions alongside scheduling decisions.

The main improvement over Phase 1 is the use of optional intervals and alternative constraints to represent multiple eligible machines without explicitly encoding pairwise Big-M sequencing constraints.