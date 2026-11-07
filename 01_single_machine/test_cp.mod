
using CP;

range Jobs = 1..3;
int duration[Jobs] = [4, 6, 3];

dvar interval task[j in Jobs] size duration[j];

minimize max(j in Jobs) endOf(task[j]);

subject to {
    noOverlap(task);
}

execute {
    writeln("Optimal schedule:");
    for(var j in Jobs) {
        writeln("Job ", j,
                ": Start = ", task[j].start,
                ", End = ", task[j].end);
    }
}
