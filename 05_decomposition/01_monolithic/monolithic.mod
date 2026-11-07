using CP;

/* Phase 5 baseline: monolithic CP wafer-lot scheduling.
 * Input: benchmark_30.dat (deterministically generated synthetic data).
 * Objective: weighted tardiness, with makespan as a tie-breaker.
 */
int nLots = ...;
int nOps = ...;
int nTools = ...;
int horizon = ...;
range Lots = 1..nLots;
range Ops = 1..nOps;
range Tools = 1..nTools;

int release[Lots] = ...;
int due[Lots] = ...;
int weight[Lots] = ...;

tuple Choice {
    int lot;
    int op;
    int tool;
    int duration;
}
{Choice} choices = ...;

tuple Maintenance {
    int tool;
    int start;
    int finish;
}
{Maintenance} maintenance = ...;

dvar interval op[j in Lots][o in Ops] in release[j]..horizon;
dvar interval assign[c in choices] optional in release[c.lot]..horizon size c.duration;

dexpr int completion[j in Lots] = endOf(op[j][nOps]);
dexpr int tardiness[j in Lots] = maxl(0, completion[j] - due[j]);

dexpr int weightedTardiness =
    sum(j in Lots) weight[j] * tardiness[j];

dexpr int makespan =
    max(j in Lots) completion[j];

// Configure CP Optimizer before solving.
execute {
    cp.param.TimeLimit = 5;
    cp.param.Workers = 4;
    cp.param.TimeMode = "ElapsedTime";
}

// Only ONE objective statement.
minimize (horizon+1) * weightedTardiness + makespan;

subject to {
    forall(j in Lots, o in Ops)
        alternative(
            op[j][o],
            all(c in choices:
                c.lot == j && c.op == o)
                assign[c]
        );

    forall(j in Lots, o in 1..nOps-1)
        endBeforeStart(op[j][o], op[j][o+1]);

    forall(m in Tools)
        sum(c in choices: c.tool == m)
            pulse(assign[c], 1)
        + sum(d in maintenance: d.tool == m)
            pulse(d.start, d.finish, 1) <= 1;
}

// Print the solution after solving.
execute {
    writeln("SUMMARY,", weightedTardiness, ",", makespan);

    for(var j in Lots) {
        writeln("LOT,", j, ",",
                release[j], ",",
                due[j], ",",
                weight[j], ",",
                op[j][nOps].end);
    }

    for(var c in choices) {
        if(assign[c].present) {
            writeln("ASSIGN,", c.lot, ",",
                    c.op, ",",
                    c.tool, ",",
                    assign[c].start, ",",
                    assign[c].end);
        }
    }
}
