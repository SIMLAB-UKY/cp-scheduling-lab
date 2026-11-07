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
