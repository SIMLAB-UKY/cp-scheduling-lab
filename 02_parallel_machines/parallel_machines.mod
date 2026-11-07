
using CP;

/*
 * Phase 2: Identical Parallel-Machine Scheduling
 *
 * Assign five jobs to two identical machines.
 * Each job must execute exactly once.
 * A machine processes at most one job at a time.
 *
 * Objective: Minimize makespan.
 */

// 1. Input data
int nJobs = 5;
int nMachines = 2;

range Jobs = 1..nJobs;
range Machines = 1..nMachines;

int duration[Jobs] = [4, 6, 3, 5, 2];

// 2. Decision variables

// Mandatory processing interval for every job.
dvar interval job[j in Jobs] size duration[j];

// Optional interval for each job-machine pair.
// The solver selects which machine executes each job.
dvar interval onMachine[j in Jobs][m in Machines]
    optional size duration[j];

// 3. Objective
minimize max(j in Jobs) endOf(job[j]);

// 4. Constraints
subject to {

    // Each job must run on exactly one machine.
    forall(j in Jobs)
        alternative(job[j],
            all(m in Machines) onMachine[j][m]);

    // Each machine processes at most one job at a time.
    forall(m in Machines)
        noOverlap(
            all(j in Jobs) onMachine[j][m]);
}

// 5. Solution reporting
execute {
    writeln("OPTIMAL SCHEDULE");

    for(var m in Machines) {
        writeln("Machine ", m, ":");

        for(var j in Jobs) {
            if(onMachine[j][m].present) {
                writeln("  Job ", j,
                        ": Start = ", onMachine[j][m].start,
                        ", End = ", onMachine[j][m].end);
            }
        }
    }
}
