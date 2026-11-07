
using CP;

/*
 * Phase 3: Flexible Job-Shop Scheduling
 *
 * Three jobs, two operations per job, three tools.
 * Each operation selects one eligible tool.
 * Operations within each job must follow their order.
 * Tools cannot process overlapping operations.
 *
 * Objective: Minimize makespan.
 */

int nJobs = 3;
int nOps = 2;
int nMachines = 3;

range Jobs = 1..nJobs;
range Ops = 1..nOps;
range Machines = 1..nMachines;

// Eligible assignments and their processing times
tuple Choice {
    int j;
    int o;
    int m;
    int p;
}

{Choice} choices = {
    <1,1,1,3>, <1,1,2,5>,
    <1,2,2,4>, <1,2,3,6>,

    <2,1,1,4>, <2,1,3,3>,
    <2,2,2,5>, <2,2,3,4>,

    <3,1,2,2>, <3,1,3,4>,
    <3,2,1,3>, <3,2,3,5>
};

// Mandatory interval for each operation
dvar interval operation[j in Jobs][o in Ops];

// Optional interval for each eligible assignment
dvar interval assignment[c in choices]
    optional size c.p;

// Objective: minimize completion of the final job
minimize max(j in Jobs) endOf(operation[j][nOps]);

subject to {

    // Select exactly one eligible machine
    // for every operation
    forall(j in Jobs, o in Ops)
        alternative(
            operation[j][o],
            all(c in choices: c.j == j && c.o == o)
                assignment[c]
        );

    // Precedence within each job
    forall(j in Jobs, o in 1..nOps-1)
        endBeforeStart(
            operation[j][o],
            operation[j][o+1]
        );

    // Machine capacity: no overlapping operations
    forall(m in Machines)
        noOverlap(
            all(c in choices: c.m == m)
                assignment[c]
        );
}

// Print the resulting schedule
execute {
    writeln("FLEXIBLE JOB SHOP SCHEDULE");

    for(var m in Machines) {
        writeln("Machine ", m);

        for(var c in choices) {
            if(c.m == m && assignment[c].present) {
                writeln(
                    "  Job ", c.j,
                    " Op ", c.o,
                    " Start: ", assignment[c].start,
                    " End: ", assignment[c].end
                );
            }
        }
    }
}
