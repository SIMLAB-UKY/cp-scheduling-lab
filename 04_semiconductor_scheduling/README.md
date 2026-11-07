# Phase 4 — Semiconductor Fab Scheduling

## Overview

A synthetic semiconductor scheduling problem developed using IBM ILOG CP Optimizer and Optimization Programming Language (OPL).

This phase extends flexible job-shop scheduling to include release times, deadlines, priority weights, maintenance constraints, and reentrant processing.

## Problem Definition

- 3 wafer lots
- 3 processing steps per lot
- 3 processing tools
- Tool-dependent processing durations
- Alternative eligible tools
- Preventive maintenance on Tool M2 during time interval [5,8)

Each lot must complete its operations in the prescribed order. Operations are non-preemptive, and each tool has capacity one.

## Optimization Objective

Minimize total weighted tardiness, then minimize makespan among schedules with equal weighted tardiness.

For each lot:

\[
T_j = \max(0,C_j-d_j)
\]

Primary objective:

\[
\min \sum_j w_j T_j
\]

A combined integer objective is used to enforce the priority between tardiness and makespan within the bounded scheduling horizon.

## CP Optimizer Concepts

- Mandatory and optional interval variables
- `alternative` for machine assignment
- `endBeforeStart` for operation precedence
- `pulse` for capacity and maintenance restrictions
- `endOf` for completion times
- Weighted tardiness objectives

## Verification Plan

1. Every operation must be scheduled exactly once.
2. Every selected tool must be eligible.
3. Operations must respect the lot route.
4. No two operations may overlap on one tool.
5. Tool M2 must remain unavailable during maintenance.
6. Lot release times and processing durations must be satisfied.
7. The reported objective must match the final schedule.

## Experiments

- Baseline scheduling instance
- Maintenance removal
- Increased priority for Lot 1
- Reduced scheduling horizon

## Run

From the repository root:

```powershell
oplrun .\04_semiconductor_scheduling\fab_scheduler.mod
```

## Results

IBM CP Optimizer 22.2 produced the following optimal solution:

| Metric | Result |
|---|---:|
| Objective value | 17 |
| Best bound | 17 |
| Optimality gap | 0% |
| Weighted tardiness | 0 |
| Makespan | 17 time units |
| Solve time | 0.05 seconds |
| Solver variables | 27 |
| Solver constraints | 21 |

### Lot Completion

| Lot | Release | Due | Completion | Tardiness |
|---|---:|---:|---:|---:|
| L1 | 0 | 11 | 11 | 0 |
| L2 | 2 | 14 | 14 | 0 |
| L3 | 4 | 17 | 17 | 0 |

### Verification

All nine operations were assigned to eligible tools. Each lot followed its required operation sequence, and no tool processed overlapping operations. Tool M2 was unavailable during its maintenance period from time 5 to 8.

The reported objective and best bound were both 17, confirming global optimality under the specified model.

## Limitations

This is an educational scheduling benchmark with synthetic inputs. It is not an Intel production model.

Future extensions will address batching, setup times, queue-dependent decisions, rolling-horizon scheduling, stochastic operation durations, and decomposition.