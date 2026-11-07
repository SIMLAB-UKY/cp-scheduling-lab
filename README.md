# CP Scheduling Lab

Industrial scheduling and resource optimization using
IBM ILOG CP Optimizer and OPL.

## Tools
- IBM CPLEX Optimization Studio 22.2
- CP Optimizer
- OPL
- Visual Studio Code

## Roadmap
1. Single-machine scheduling
2. Parallel-machine scheduling
3. Flexible job-shop scheduling
4. Semiconductor manufacturing scheduling
5. Decomposition methods
6. Model verification and benchmarking

## Phase 1: Single-machine scheduling
Three jobs with processing times 4, 6, and 3.

Objective: minimize makespan.

Verified optimal makespan: 13 time units.

## Run
Use the IBM OPL command-line runner:

    oplrun 01_single_machine/test_cp.mod


## Completed Phases

### Phase 1 — Single-Machine Scheduling

**Problem:** Schedule three jobs on one machine to minimize makespan.

**CP concepts:** `dvar interval`, `endOf`, `noOverlap`.

**Result:** Optimal makespan = 13 time units (verified with CP Optimizer).

**Source:** [`01_single_machine/test_cp.mod`](01_single_machine/test_cp.mod)

### Phase 2 — Parallel-Machine Scheduling

**Problem:** Assign five jobs to two identical parallel machines and determine their processing sequences.

**CP concepts:** Optional interval variables, `alternative`, `noOverlap`.

**Objective:** Minimize makespan.

**Benchmark:** Total processing time = 20 units. A feasible schedule with makespan 10 achieves the lower bound of 10, proving optimality.

**Source:** [`02_parallel_machines/parallel_machines.mod`](02_parallel_machines/parallel_machines.mod)

### Phase 3 — Flexible Job-Shop Scheduling

**Problem:** Schedule three jobs, each with two sequential operations, across three tools with different processing times and eligibility restrictions.

**CP concepts:** Tuple-based data structures, optional intervals, `alternative`, `endBeforeStart`, `noOverlap`.

**Objective:** Minimize makespan.

**Benchmark:** Optimal makespan = 7 time units, established by a feasible schedule and a critical-path lower bound.

**Source:** [`03_flexible_job_shop/flexible_job_shop.mod`](03_flexible_job_shop/flexible_job_shop.mod)

## Upcoming Work

**Phase 4:** Semiconductor scheduling with lot release times, due dates, priorities, maintenance windows, and reentrant processing.

**Phase 5:** Decomposition methods for large-scale scheduling.

**Phase 6:** Independent model verification, benchmarking, and computational experiments.

## Running the Models

Models are written in IBM Optimization Programming Language (OPL) and solved using CP Optimizer 22.2.

From the repository root:

```powershell
oplrun .\01_single_machine\test_cp.mod
oplrun .\02_parallel_machines\parallel_machines.mod
oplrun .\03_flexible_job_shop\flexible_job_shop.mod
```

The IBM OPL executable must be installed and available on PATH.

## Validation Approach

Each phase is verified through:

1. Solver feasibility and solution status.
2. Independent checking of assignments and scheduling constraints.
3. Comparison against analytical lower bounds.
4. Inspection of makespan and scheduled start/end times.


