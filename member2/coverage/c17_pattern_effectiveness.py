import json
import sys
from pathlib import Path


# ============================================================
# 1. CHECK INPUT
# ============================================================

if len(sys.argv) < 2:
    print("Usage:")
    print("python pattern_effectiveness.py <simulation_results.json>")
    sys.exit(1)


INPUT_FILE = Path(sys.argv[1])


# ============================================================
# 2. READ SIMULATION RESULTS
# ============================================================

with open(INPUT_FILE, "r") as file:
    results = json.load(file)


# ============================================================
# 3. DETERMINE BENCHMARK
# ============================================================

benchmark_name = INPUT_FILE.stem.replace(
    "_simulation_results",
    ""
)


# ============================================================
# 4. REVERSE FAULT → PATTERNS
#    INTO PATTERN → FAULTS
# ============================================================

pattern_faults = {}


for result in results:

    fault_id = result["fault_id"]

    detected_patterns = result.get(
        "detected_patterns",
        []
    )

    for pattern in detected_patterns:

        if pattern not in pattern_faults:
            pattern_faults[pattern] = []

        pattern_faults[pattern].append(
            fault_id
        )


# ============================================================
# 5. CREATE EFFECTIVENESS LIST
# ============================================================

effectiveness = []


for pattern, faults in pattern_faults.items():

    effectiveness.append({

        "pattern":
            pattern,

        "detected_faults":
            faults,

        "fault_count":
            len(faults)
    })


# ============================================================
# 6. SORT MOST EFFECTIVE FIRST
# ============================================================

effectiveness.sort(
    key=lambda x: x["fault_count"],
    reverse=True
)


# ============================================================
# 7. SAVE
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    BASE_DIR
    / "member2"
    / "data"
    / f"{benchmark_name}_pattern_effectiveness.json"
)


with open(
    OUTPUT_FILE,
    "w"
) as file:

    json.dump(
        effectiveness,
        file,
        indent=4
    )


# ============================================================
# 8. DISPLAY
# ============================================================

print()
print("VISTA Pattern Effectiveness")
print("===========================")
print()

print(
    "Benchmark:",
    benchmark_name
)

print(
    "Patterns that detect faults:",
    len(effectiveness)
)

print()

print("Top 10 patterns:")
print("----------------")


for item in effectiveness[:10]:

    print(
        item["pattern"],
        "| Faults detected:",
        item["fault_count"]
    )


print()
print("Pattern effectiveness saved to:")
print(OUTPUT_FILE)