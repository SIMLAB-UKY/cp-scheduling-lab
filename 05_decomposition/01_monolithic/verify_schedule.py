"""Independently check a CP Optimizer scheduling output against the synthetic .dat instance."""
from __future__ import annotations
import argparse
import re
from pathlib import Path


def read_instance(path: Path):
    data = path.read_text(encoding="utf-8")
    def arr(name):
        match = re.search(rf"\b{name}\s*=\s*\[([^]]+)\]", data)
        if not match:
            raise ValueError(f"Missing {name}")
        return [int(s) for s in re.findall(r"\d+", match.group(1))]
    choices = {}
    maintenance = []
    choice_block = data.split("choices = {", 1)[1].split("};", 1)[0]
    for a, b, c, d in re.findall(r"<(\d+),(\d+),(\d+),(\d+)>", choice_block):
        choices[int(a), int(b), int(c)] = int(d)
    maintenance_block = data.split("maintenance = {", 1)[1].split("};", 1)[0]
    maintenance = [tuple(map(int, x)) for x in re.findall(r"<(\d+),(\d+),(\d+)>", maintenance_block)]
    return arr("release"), arr("due"), arr("weight"), choices, maintenance


def check(data_path: Path, log_path: Path):
    release, due, weight, eligible, maintenance = read_instance(data_path)
    # Support PowerShell 5.1 UTF-16 logs and UTF-8 logs.
    raw_bytes = log_path.read_bytes()
    if raw_bytes.startswith((b"\xff\xfe", b"\xfe\xff")):
        log = raw_bytes.decode("utf-16")
    elif b"\x00" in raw_bytes[:200]:
        log = raw_bytes.decode("utf-16-le")
    else:
        log = raw_bytes.decode("utf-8-sig", errors="replace")
    assignments = {}
    tools = {m: [] for _,_,m in eligible}
    lots = {}
    summary = None
    for raw in log.splitlines():
        line = raw.strip()
        if line.startswith("ASSIGN,"):
            _, j, o, m, s, e = line.split(",")
            j,o,m,s,e = map(int,(j,o,m,s,e))
            assert (j,o) not in assignments, f"Duplicate operation {(j,o)}"
            assert (j,o,m) in eligible, f"Ineligible machine for {(j,o)}: {m}"
            assert e-s == eligible[j,o,m], f"Bad duration for {(j,o)}"
            assert s >= release[j-1], f"Released late: lot {j}"
            assignments[j,o] = (m,s,e)
            tools[m].append((s,e,f"lot {j} op {o}"))
        elif line.startswith("LOT,"):
            _,j,r,d,w,c = line.split(",")
            lots[int(j)] = tuple(map(int,(r,d,w,c)))
        elif line.startswith("SUMMARY,"):
            _,wt,ms = line.split(",")
            summary = (int(wt),int(ms))
    assert summary is not None, "No SUMMARY found (did solver produce a solution?)"
    assert len(assignments) == 3*len(release), f"Expected {3*len(release)} assignments, got {len(assignments)}"
    assert len(lots) == len(release)
    for j in range(1,len(release)+1):
        for o in (1,2):
            assert assignments[j,o][2] <= assignments[j,o+1][1], f"Precedence failure lot {j}"
        assert lots[j] == (release[j-1],due[j-1],weight[j-1],assignments[j,3][2]), f"Lot summary mismatch {j}"
    for m,s,e in maintenance:
        tools.setdefault(m, []).append((s,e,"MAINTENANCE"))
    for m, spans in tools.items():
        spans.sort()
        for before,after in zip(spans,spans[1:]):
            assert before[1] <= after[0], f"Tool {m} overlap: {before} / {after}"
    wt = sum(weight[j-1]*max(0,assignments[j,3][2]-due[j-1]) for j in range(1,len(release)+1))
    ms = max(assignments[j,3][2] for j in range(1,len(release)+1))
    assert (wt,ms) == summary, f"Objective components mismatch: computed {(wt,ms)}, output {summary}"
    assert ms <= 350, "Out of horizon"
    print(f"PASS: {len(assignments)} operations; {len(tools)} tools; weighted tardiness={wt}; makespan={ms}")
    print(f"Combined objective={(350+1)*wt+ms}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, default=Path(__file__).with_name("benchmark_30.dat"))
    p.add_argument("--log", type=Path, required=True)
    a = p.parse_args()
    check(a.data, a.log)
