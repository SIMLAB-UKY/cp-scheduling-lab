"""Generate a deterministic synthetic 30-lot CP scheduling benchmark."""
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent
RNG = random.Random(20261106)
N_LOTS, N_OPS, N_TOOLS = 30, 3, 5
HORIZON = 350

# Some process steps return to tool families used earlier (reentrant flow).
ELIGIBLE = {1: [1, 3], 2: [2, 4, 5], 3: [1, 3, 5]}
release = [RNG.randrange(0, 45, 3) for _ in range(N_LOTS)]
due = [release[j] + RNG.randint(24, 43) for j in range(N_LOTS)]
weight = [RNG.choice([1, 1, 2, 3, 5]) for _ in range(N_LOTS)]
choices = []
for j in range(1, N_LOTS+1):
    for op in range(1, N_OPS+1):
        base = RNG.randint(4, 8)
        for tool in ELIGIBLE[op]:
            choices.append((j, op, tool, base + ((j + 2*op + tool) % 3)))

# Include fixed downtime windows for two tools.
maintenance = [(2, 30, 43), (4, 75, 90)]
lines = [
    f"nLots = {N_LOTS};", f"nOps = {N_OPS};", f"nTools = {N_TOOLS};",
    f"horizon = {HORIZON};", "release = [" + ", ".join(map(str, release)) + "];",
    "due = [" + ", ".join(map(str, due)) + "];",
    "weight = [" + ", ".join(map(str, weight)) + "];",
    "choices = {", *[f"  <{j},{o},{m},{p}>{',' if i < len(choices)-1 else ''}" for i, (j,o,m,p) in enumerate(choices)],
    "};", "maintenance = {", *[f"  <{m},{s},{e}>{',' if i < len(maintenance)-1 else ''}" for i,(m,s,e) in enumerate(maintenance)], "};"
]
(ROOT / "benchmark_30.dat").write_text("\n".join(lines)+"\n", encoding="utf-8")
print(f"Generated {N_LOTS} lots, {len(choices)} eligible assignments, {len(maintenance)} maintenance windows")
