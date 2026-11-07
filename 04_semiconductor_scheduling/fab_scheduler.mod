
using CP;

/*
 * Phase 4 - Semiconductor Fab Scheduling
 *
 * 3 wafer lots, 3 operations per lot, 3 tools.
 * Includes tool eligibility, release times, due dates,
 * priority weights, maintenance and reentrant routing.
 *
 * Objective: weighted tardiness, then makespan.
 */

// ---------- DATA ----------

range Lots = 1..3;
range Ops = 1..3;
range Tools = 1..3;

int horizon = 30;

int release[Lots] = [0, 2, 4];
int due[Lots] = [11, 14, 17];
int weight[Lots] = [3, 2, 1];

tuple Choice {
    int lot;
    int op;
    int tool;
    int duration;
}

{Choice} choices = {
    <1,1,1,3>, <1,1,3,4>,
    <1,2,2,4>, <1,2,3,6>,
    <1,3,1,2>, <1,3,3,3>,

    <2,1,1,4>, <2,1,3,5>,
    <2,2,2,3>, <2,2,3,4>,
    <2,3,1,3>, <2,3,3,4>,

    <3,1,1,2>, <3,1,3,3>,
    <3,2,2,5>, <3,2,3,4>,
    <3,3,1,3>, <3,3,3,4>
};

// ---------- VARIABLES ----------

// Mandatory operation intervals
dvar interval op[j in Lots][o in Ops]
    in release[j]..horizon;

// Optional tool-specific intervals
dvar interval assign[c in choices]
    optional in release[c.lot]..horizon
    size c.duration;

// ---------- EXPRESSIONS ----------

dexpr int completion[j in Lots] =
    endOf(op[j][3]);

dexpr int tardiness[j in Lots] =
    maxl(0, completion[j] - due[j]);

dexpr int totalWeightedTardiness =
    sum(j in Lots) weight[j] * tardiness[j];

dexpr int makespan =
    max(j in Lots) completion[j];

// ---------- OBJECTIVE ----------

// Makespan <= 30, so 100 gives strict priority
// to the integer-valued weighted tardiness.
minimize 100 * totalWeightedTardiness + makespan;

// ---------- CONSTRAINTS ----------

subject to {

    // Choose exactly one eligible tool for each operation.
    forall(j in Lots, o in Ops)
        alternative(
            op[j][o],
            all(c in choices:
                c.lot == j && c.op == o)
                assign[c]
        );

    // Enforce the lot process route.
    forall(j in Lots, o in 1..2)
        endBeforeStart(op[j][o], op[j][o+1]);

    // Tools M1 and M3: at most one operation at a time.
    forall(m in Tools: m != 2)
        sum(c in choices: c.tool == m)
            pulse(assign[c], 1) <= 1;

    // M2 is also unavailable during maintenance [5,8).
    sum(c in choices: c.tool == 2)
        pulse(assign[c], 1)
        + pulse(5, 8, 1) <= 1;
}

// ---------- SOLUTION REPORT ----------

execute {
    writeln("=== FAB SCHEDULING ===");

    writeln("Objective: ",
        100 * totalWeightedTardiness + makespan);
    writeln("Weighted tardiness: ",
        totalWeightedTardiness);
    writeln("Makespan: ", makespan);

    writeln();
    writeln("LOT RESULTS");

    for(var j in Lots) {
        writeln("Lot ", j,
            " Release=", release[j],
            " Due=", due[j],
            " Completion=", op[j][3].end,
            " Tardiness=",
            Math.max(0, op[j][3].end - due[j]));
    }

    writeln();
    writeln("TOOL SCHEDULES");

    for(var m in Tools) {
        writeln("Tool ", m);

        for(var c in choices) {
            if(c.tool == m && assign[c].present) {
                writeln(
                    "  Lot ", c.lot,
                    " Op ", c.op,
                    " Start=", assign[c].start,
                    " End=", assign[c].end
                );
            }
        }

        if(m == 2)
            writeln("  Maintenance [5,8)");
    }
}
