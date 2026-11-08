# CP Scheduling Lab

**Industrial Scheduling, Constraint Programming, and Optimization Decomposition**

A hands-on operations research portfolio focused on industrial scheduling, resource allocation, and optimization using **IBM ILOG CP Optimizer, Optimization Programming Language (OPL), and Python**.

The project progresses from fundamental scheduling models to semiconductor manufacturing scheduling, large-scale constraint programming, decomposition methods, and independent computational benchmarking.

The emphasis is on developing **correct, reproducible, and computationally practical optimization models**, rather than simply obtaining solver solutions.

## 1. Project Objectives

- Develop proficiency in IBM OPL and CP Optimizer.
- Formulate and solve single-machine, parallel-machine, and flexible job-shop scheduling problems.
- Model semiconductor manufacturing constraints, including tool eligibility, operation precedence, maintenance, and reentrant flows.
- Investigate scheduling under release times, due dates, and competing priorities.
- Compare monolithic constraint programming with decomposition-based scheduling approaches.
- Independently verify optimization solutions.
- Evaluate computational performance using reproducible experiments and consistent metrics.

## 2. Technology Stack

| Technology | Application |
|---|---|
| IBM CPLEX Optimization Studio 22.2 | Optimization development environment |
| IBM CP Optimizer | Constraint programming and scheduling |
| OPL | Optimization modeling language |
| Python | Benchmark generation, orchestration, verification, and analysis |
| Visual Studio Code | Development environment |
| Git and GitHub | Version control and reproducibility |

## 3. Repository Structure

```text
cp-scheduling-lab/
│
├── 01_single_machine/
│   └── test_cp.mod
│
├── 02_parallel_machines/
│   ├── parallel_machines.mod
│   └── README.md
│
├── 03_flexible_job_shop/
│   ├── flexible_job_shop.mod
│   └── README.md
│
├── 04_semiconductor_scheduling/
│   ├── fab_scheduler.mod
│   └── README.md
│
├── 05_decomposition/
│   ├── 01_monolithic/
│   │   ├── monolithic.mod
│   │   ├── benchmark_30.dat
│   │   ├── generate_instance.py
│   │   ├── verify_schedule.py
│   │   └── README.md
│   │
│   └── 02_lot_decomposition/
│       ├── subproblem.mod
│       ├── run_decomposition.py
│       ├── test_decomposition.py
│       └── README.md
│
├── 06_verification_benchmarking/
│   ├── benchmark.py
│   ├── test_benchmark.py
│   ├── README.md
│   └── results/
│       ├── results.md
│       ├── results.csv
│       └── results.json
│
└── README.md
```

Generated benchmark results may be excluded from version control depending on the local `.gitignore` configuration.

## 4. Project Roadmap

| Phase | Description | Status | Main Result |
|---|---|---|---|
| 1 | Single-machine scheduling | Complete | Optimal makespan: 13 |
| 2 | Parallel-machine scheduling | Complete | Analytical optimum: 10 |
| 3 | Flexible job-shop scheduling | Complete | Analytical optimum: 7 |
| 4 | Semiconductor manufacturing scheduling | Complete | Zero tardiness; optimal makespan: 17 |
| 5A | Monolithic CP scheduling | Complete | Verified 30-lot solution |
| 5B | Lot-based CP decomposition | Complete | Working decomposed scheduler |
| 6 | Independent verification and benchmarking | Complete | Four verified benchmark configurations |

---

## 5. Phase 1 — Single-Machine Scheduling

### Problem

Schedule three independent jobs on a single machine with processing times of 4, 6, and 3 time units.

**Objective:** Minimize makespan.

### CP Concepts

- `dvar interval` — Processing activities
- `endOf` — Completion times
- `noOverlap` — Exclusive resource use

### Results

CP Optimizer proved an optimal makespan of **13 time units**, with a zero optimality gap.

**Key learning:** Scheduling can be represented directly through interval variables without explicit binary sequencing decisions.

[View Phase 1 model](01_single_machine/test_cp.mod)

## 6. Phase 2 — Parallel-Machine Scheduling

### Problem

Assign five jobs to two identical machines while determining their processing sequences.

Each job must execute exactly once without interruption.

### CP Concepts

- Mandatory and optional interval variables
- `alternative` for machine selection
- `noOverlap` for resource capacity

### Results

Total processing workload: 20 time units.

With two machines, the workload lower bound is:

\[
C_{\max} \geq \left\lceil \frac{20}{2} \right\rceil = 10
\]

A feasible schedule achieves makespan **10**, establishing global optimality for this instance.

**Key learning:** Constraint programming can jointly optimize machine assignment and operation scheduling.

[View Phase 2](02_parallel_machines/README.md)

## 7. Phase 3 — Flexible Job-Shop Scheduling

### Problem

Schedule three jobs, each containing two sequential operations, across three machines.

Operations have different processing times depending on the selected machine, and not every machine is eligible for every operation.

### CP Concepts

- Tuple-based eligibility data
- Optional processing intervals
- `alternative`
- `endBeforeStart`
- `noOverlap`

### Results

An analytically established optimal schedule achieves makespan **7 time units**.

**Key learning:** Flexible job-shop scheduling combines equipment eligibility, resource assignment, technological precedence, and sequencing.

[View Phase 3](03_flexible_job_shop/README.md)

## 8. Phase 4 — Semiconductor Manufacturing Scheduling

### Problem

A synthetic semiconductor fab scheduling instance consisting of:

- 3 wafer lots
- 3 sequential processing operations per lot
- 3 manufacturing tools
- Tool-specific processing times
- Alternative eligible tools
- Lot release times and due dates
- Priority weights
- Preventive maintenance
- Reentrant processing

### Optimization Objective

Minimize total weighted tardiness, using makespan as a secondary objective.

For lot \(j\):

\[
T_j = \max(0,C_j-d_j)
\]

The primary objective is:

\[
\min \sum_j w_j T_j
\]

### Results

| Metric | Value |
|---|---:|
| Wafer lots | 3 |
| Operations | 9 |
| Tools | 3 |
| Weighted tardiness | 0 |
| Optimal makespan | 17 |
| Combined objective | 17 |
| Solver time | 0.05 seconds |
| Optimality gap | 0% |

The solution satisfied all lot precedence, tool eligibility, maintenance, and machine capacity constraints.

**Key learning:** CP Optimizer can integrate scheduling, resource eligibility, maintenance, and multi-priority operational requirements in one model.

[View Phase 4](04_semiconductor_scheduling/README.md)

---

## 9. Phase 5 — Large-Scale Scheduling and Decomposition

Phase 5 extends the earlier scheduling models to a larger synthetic semiconductor manufacturing benchmark.

### Benchmark Instance

| Parameter | Value |
|---|---:|
| Wafer lots | 30 |
| Operations per lot | 3 |
| Total operations | 90 |
| Manufacturing tools | 5 |
| Solver | IBM CP Optimizer 22.2 |
| Optimization objective | Weighted tardiness, then makespan |

The scheduling model incorporates processing precedence, alternative eligible tools, machine capacity, maintenance windows, release times, and due dates.

### Phase 5A — Monolithic CP

The complete scheduling problem is solved simultaneously using CP Optimizer.

For the initial five-second search:

| Metric | Value |
|---|---:|
| Weighted tardiness | 1,363 |
| Makespan | 151 |
| Combined objective | 478,564 |
| Solver time | 5.01 seconds |
| Best bound | 66 |
| Optimality proven | No |
| Independent verification | PASS |

The solver produced a feasible schedule but did not establish global optimality within the time limit.

**Key learning:** A feasible optimization solution and a proven optimal solution are fundamentally different. Solution quality must be distinguished from solver bounds and convergence.

[View Phase 5A](05_decomposition/01_monolithic/README.md)

### Phase 5B — Lot-Based CP Decomposition

A decomposition-based scheduler was implemented using lot-based Large Neighborhood Search (LNS).

The approach:

1. Constructs a greedy feasible schedule.
2. Selects a subset of lots for re-optimization.
3. Fixes the schedules of non-selected lots.
4. Solves the smaller CP subproblem.
5. Accepts feasible improvements.
6. Repeats across selected neighborhoods.

All resulting schedules are checked against the complete set of original scheduling constraints.

An initial decomposition experiment reduced the greedy combined objective from 789,598 to 602,124, an improvement of approximately **23.7%**.

However, the decomposed scheduler did not outperform the monolithic model on the tested benchmark.

**Key learning:** Decomposition requires effective coordination between subproblems. Fixing too many existing decisions can prevent the algorithm from discovering better global schedules.

[View Phase 5B](05_decomposition/02_lot_decomposition/README.md)

---

## 10. Phase 6 — Independent Verification and Benchmarking

**Status: Completed**

Phase 6 establishes a reproducible experimental framework for comparing monolithic CP with lot-based decomposition.

### Experimental Setup

Both methods were evaluated on the same synthetic 30-lot scheduling problem, using nominal computational budgets of 5 and 30 seconds.

The benchmarking framework:

- Measures end-to-end wall-clock runtime.
- Independently verifies each schedule.
- Recalculates weighted tardiness and makespan.
- Records combined objective values.
- Produces CSV, JSON, and Markdown reports.
- Includes automated unit tests.

Six Python unit tests passed.

### Final Benchmark Results

| Method | Budget | Wall Time (s) | Weighted Tardiness | Makespan | Combined Objective | Verified |
|---|---:|---:|---:|---:|---:|---|
| Monolithic CP | 5s | 5.049 | 1,363 | 151 | **478,564** | PASS |
| Lot Decomposition | 5s | 4.138 | 2,012 | 199 | 706,411 | PASS |
| Monolithic CP | 30s | 30.042 | 1,339 | 151 | **470,140** | PASS |
| Lot Decomposition | 30s | 29.577 | 1,620 | 158 | 568,778 | PASS |

All four schedules passed independent verification.

### Key Findings

**1. Monolithic CP produced better solutions at both time budgets.**

The monolithic model achieved lower weighted tardiness and makespan than the decomposition method.

At the nominal 30-second budget, monolithic CP achieved a combined objective approximately **17.3% lower** than the decomposed approach.

**2. Additional computation improved the monolithic solution.**

Increasing the search limit from 5 to 30 seconds reduced the combined objective from 478,564 to 470,140.

**3. Decomposition improved feasible schedules but struggled with global coordination.**

The approach successfully improved its initial greedy schedule, but fixed reservations outside the selected neighborhood limited its ability to find better solutions.

**4. Independent verification was essential.**

All reported schedules were verified for assignment completeness, tool eligibility, processing durations, precedence, resource conflicts, release times, maintenance, and objective consistency.

**5. Computational comparison requires careful experimental design.**

Both methods were evaluated using measured end-to-end wall-clock time. However, nominal solver limits and decomposition budgets do not guarantee identical execution durations.

### Limitations

- The experiments use a single synthetic scheduling benchmark.
- Each reported configuration represents one trial.
- Repeated executions showed consistent objective values, but multi-instance statistical analysis was not conducted.
- The decomposition implementation uses fixed outside-neighborhood operations and a greedy initial solution.
- Neither method established global optimality for the 30-lot instance.
- Results should not be generalized to all semiconductor scheduling problems.

### Reproducibility

From the `06_verification_benchmarking` folder:

```powershell
python .\test_benchmark.py
python .\benchmark.py --budgets 5 30 --trials 1
```

Generated reports:

```text
results/results.md
results/results.csv
results/results.json
```

[View Phase 6](06_verification_benchmarking/README.md)

---

## 11. Running the Models

### Requirements

- IBM CPLEX Optimization Studio 22.2
- IBM CP Optimizer
- OPL command-line runner (`oplrun`)
- Python 3
- Windows PowerShell or a compatible terminal

### Basic Scheduling Models

From the repository root:

```powershell
oplrun .\01_single_machine\test_cp.mod
oplrun .\02_parallel_machines\parallel_machines.mod
oplrun .\03_flexible_job_shop\flexible_job_shop.mod
oplrun .\04_semiconductor_scheduling\fab_scheduler.mod
```

If `oplrun` is not available on PATH, use its installed executable location.

### Monolithic CP Benchmark

```powershell
cd .\05_decomposition\01_monolithic

oplrun .\monolithic.mod .\benchmark_30.dat |
    Tee-Object -FilePath .\run_30.log

python .\verify_schedule.py --log .\run_30.log
```

On Windows PowerShell, ensure the log encoding is compatible with the verifier.

### Decomposition Benchmark

From `05_decomposition/02_lot_decomposition`:

```powershell
python .\test_decomposition.py

python .\run_decomposition.py --budget 30 --batch-size 10 --subproblem-seconds 5 --max-subproblems 6 --output .\decomposed_30s.log

python ..\01_monolithic\verify_schedule.py --data ..\01_monolithic\benchmark_30.dat --log .\decomposed_30s.log
```

### Complete Benchmark Suite

From `06_verification_benchmarking`:

```powershell
python .\test_benchmark.py
python .\benchmark.py --budgets 5 30 --trials 1
```

## 12. Model Verification Approach

The project emphasizes a separation between **solver correctness, schedule feasibility, and solution optimality**.

The verification framework checks:

1. Every mandatory operation is scheduled exactly once.
2. Every operation is assigned to an eligible tool.
3. Assigned processing durations match the input data.
4. Lot operations follow their required precedence.
5. No tool processes conflicting operations simultaneously.
6. Maintenance restrictions are respected.
7. Release times and scheduling horizon restrictions are satisfied.
8. Weighted tardiness and makespan are independently recomputed.
9. The combined objective matches the independently calculated value.

Solver bounds and termination status are retained separately to distinguish feasible solutions from proven optimal solutions.

## 13. Key Lessons Learned

### Constraint Programming

CP Optimizer provides expressive scheduling constructs for intervals, optional resource assignments, precedence, and capacity constraints.

These can simplify scheduling formulations compared with explicitly modeling all sequencing relationships using mixed-integer programming.

### System-Level Scheduling

A locally favorable assignment may produce poor system-wide results because multiple jobs compete for the same resources.

Machine eligibility, operation precedence, bottlenecks, and downstream dependencies must be modeled together.

### Decomposition

Breaking a large optimization problem into smaller subproblems does not guarantee improved performance.

Effective decomposition depends on subproblem selection, coordination, shared resource constraints, initial solutions, and the computational budget.

### Model Verification

An optimization model can return a feasible solution without proving optimality.

Independent verification is important for detecting formulation, implementation, and reporting errors.

### Computational Benchmarking

Optimization methods should be compared using consistent benchmark instances, reproducible settings, verified solutions, and measured computational effort.

## 14. Future Research Directions

Potential extensions include:

- Monolithic-seeded Large Neighborhood Search
- Adaptive neighborhood selection
- Benders decomposition
- Dantzig–Wolfe decomposition and column generation
- Lagrangian relaxation
- Hybrid MIP–CP optimization
- Sequence-dependent setup times
- Batch-processing equipment
- Reentrant job-shop scheduling
- Rolling-horizon rescheduling
- Tool failures and uncertain processing times
- Discrete-event simulation for closed-loop schedule validation
- Multiple benchmark instances and statistical comparison

These are future directions, not completed implementations in version 1.0.

## 15. Project Scope and Disclaimer

This repository is an educational and experimental operations research portfolio.

All semiconductor scheduling data are synthetic. The models are intended to demonstrate general industrial optimization concepts and are not representations of Intel's proprietary manufacturing processes, scheduling systems, or production data.

IBM CPLEX Optimization Studio and CP Optimizer are proprietary software products and are not distributed with this repository.

---

## Project Status

**CP Scheduling Lab — Version 1.0 Complete**

The project provides a complete progression from introductory constraint programming to semiconductor-style scheduling, large-scale optimization, decomposition, independent verification, and computational benchmarking.

The central outcome is a working and reproducible optimization workflow with documented limitations and experimentally supported results.
