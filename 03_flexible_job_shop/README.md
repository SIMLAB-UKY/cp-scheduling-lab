# Phase 3 — Flexible Job-Shop Scheduling

## 1. Problem Description

Three jobs must be processed across three machines.

Each job contains two sequential operations. Each operation can be assigned to a subset of eligible machines, with different processing times.

The optimizer determines:

- Machine assignment for each operation.
- Start and completion times.
- Operation sequences on each machine.

## 2. Input Data

| Job | Operation | Eligible Machines |
|---|---|---|
| J1 | O1 | M1: 3, M2: 5 |
| J1 | O2 | M2: 4, M3: 6 |
| J2 | O1 | M1: 4, M3: 3 |
| J2 | O2 | M2: 5, M3: 4 |
| J3 | O1 | M2: 2, M3: 4 |
| J3 | O2 | M1: 3, M3: 5 |

Processing times are in abstract time units.

## 3. Mathematical Formulation

Let \(S_{jo}\) and \(C_{jo}\) represent the start and completion times of operation \(o\) of job \(j\).

The objective is:

\[
\min C_{\max} = \max_j C_{j,2}
\]

Subject to:

**Assignment:** Each operation selects exactly one eligible machine.

**Precedence:**

\[
S_{j,2} \geq C_{j,1}
\]

**Capacity:** No two operations assigned to the same machine overlap.

**Non-preemption:** Once an operation begins, it runs until completion.

## 4. CP Optimizer Formulation

The implementation introduces:

- `tuple Choice` to represent eligible job-operation-machine combinations.
- Optional intervals for alternative processing assignments.
- `alternative` for machine selection.
- `endBeforeStart` for technological precedence.
- `noOverlap` for machine resource constraints.

The tuple-based approach avoids creating assignments for ineligible machines.

## 5. Expected Optimal Result

A critical-path lower bound is 7 time units:

- Job J1 requires at least 3 + 4 = 7 units.
- Job J2 requires at least 3 + 4 = 7 units.

A feasible schedule is:

| Machine | Operation | Start | End |
|---|---|---:|---:|
| M1 | J1-O1 | 0 | 3 |
| M1 | J3-O2 | 3 | 6 |
| M2 | J3-O1 | 0 | 2 |
| M2 | J1-O2 | 3 | 7 |
| M3 | J2-O1 | 0 | 3 |
| M3 | J2-O2 | 3 | 7 |

This schedule satisfies precedence and machine-capacity constraints, and achieves makespan 7. Therefore the optimal makespan is **7 time units**.

Confirm your OPL solver reproduces the optimal objective before reporting the execution as verified.

## 6. Verification

Check:

1. All six operations appear exactly once.
2. Each operation uses an eligible machine.
3. The processing duration matches the chosen machine.
4. Operation O1 completes before O2 begins for each job.
5. No two operations overlap on the same machine.
6. Makespan equals the maximum completion time.

## 7. Run the Model

From the repository root:

```powershell
oplrun .\03_flexible_job_shop\flexible_job_shop.mod
```

## 8. Lessons Learned

Flexible job-shop scheduling combines routing decisions and sequencing decisions.

Unlike identical parallel-machine scheduling, processing times depend on the selected resource, and each job must follow a prescribed operation sequence.

These characteristics make flexible job-shop scheduling relevant to complex manufacturing operations, including semiconductor production.