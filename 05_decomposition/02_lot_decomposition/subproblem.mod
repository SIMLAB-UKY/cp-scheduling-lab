using CP;
/*
 * Phase 5B: Optimize a selected subset of lots while reserving all
 * machine intervals belonging to the fixed lots.
 * Every operation remains non-preemptive and each selected operation
 * chooses exactly one eligible tool.
 */
int nLots = ...;
int nOps = ...;
int nTools = ...;
int horizon = ...;
int timeLimit = ...;
int workers = ...;
range Lots = 1..nLots;
range Ops = 1..nOps;
range Tools = 1..nTools;
int release[Lots] = ...;
int due[Lots] = ...;
int weight[Lots] = ...;
tuple Choice { int lot; int op; int tool; int duration; }
{Choice} choices = ...;
tuple Blocked { int tool; int start; int finish; }
{Blocked} blocked = ...;

dvar interval op[j in Lots][o in Ops] in release[j]..horizon;
dvar interval assign[c in choices] optional in release[c.lot]..horizon size c.duration;
dexpr int weightedTardiness =
    sum(j in Lots) weight[j] * maxl(0, endOf(op[j][nOps]) - due[j]);
dexpr int makespan = max(j in Lots) endOf(op[j][nOps]);

execute {
    cp.param.TimeLimit = timeLimit;
    cp.param.Workers = workers;
}
minimize (horizon + 1) * weightedTardiness + makespan;
subject to {
    forall(j in Lots, o in Ops)
        alternative(op[j][o], all(c in choices: c.lot == j && c.op == o) assign[c]);
    forall(j in Lots, o in 1..nOps-1)
        endBeforeStart(op[j][o], op[j][o+1]);
    forall(m in Tools)
        sum(c in choices: c.tool == m) pulse(assign[c], 1)
        + sum(b in blocked: b.tool == m) pulse(b.start, b.finish, 1) <= 1;
}
execute {
    writeln("LOCAL_SUMMARY,", weightedTardiness, ",", makespan);
    for(var c in choices) {
        if(assign[c].present)
            writeln("LOCAL_ASSIGN,", c.lot, ",", c.op, ",", c.tool, ",", assign[c].start, ",", assign[c].end);
    }
}
