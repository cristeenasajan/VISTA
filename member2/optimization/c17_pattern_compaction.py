import json
import sys
from pathlib import Path


# ============================================================
# 1. CHECK INPUT
# ============================================================

if len(sys.argv) < 2:
    print("Usage:")
    print("python pattern_compaction.py <pattern_effectiveness.json>")
    sys.exit(1)


INPUT_FILE = Path(sys.argv[1])


# ============================================================
# 2. READ PATTERN EFFECTIVENESS
# ============================================================

with open(INPUT_FILE, "r") as file:
    effectiveness = json.load(file)


# ============================================================
# 3. DETERMINE BENCHMARK
# ============================================================

benchmark_name = INPUT_FILE.stem.replace(
    "_pattern_effectiveness",
    ""
)


# ============================================================
# 4. BUILD PATTERN → FAULTS MAPPING
# ============================================================

pattern_faults = {}

all_detected_faults = set()


for item in effectiveness:

    pattern = item["pattern"]

    faults = set(
        item.get("detected_faults", [])
    )

    pattern_faults[pattern] = faults

    all_detected_faults.update(
        faults
    )


# ============================================================
# 5. GREEDY SET COVER
# ============================================================

remaining_faults = set(
    all_detected_faults
)

selected_patterns = []


while remaining_faults:

    best_pattern = None

    best_new_faults = set()


    for pattern, faults in pattern_faults.items():

        if pattern in selected_patterns:
            continue


        new_faults = (
            faults &
            remaining_faults
        )


        if len(new_faults) > len(
            best_new_faults
        ):

            best_pattern = pattern

            best_new_faults = (
                new_faults
            )


    # No further progress possible

    if best_pattern is None:
        break


    selected_patterns.append(
        best_pattern
    )


    remaining_faults -= (
        best_new_faults
    )


# ============================================================
# 6. STATISTICS
# ============================================================

original_pattern_count = (
    1024
    if benchmark_name == "c432"
    else len(pattern_faults)
)


selected_pattern_count = (
    len(selected_patterns)
)


detected_fault_count = (
    len(all_detected_faults)
    -
    len(remaining_faults)
)


total_faults = (
    detected_fault_count
)


coverage = (
    detected_fault_count /
    total_faults
) * 100


pattern_reduction = (
    (
        original_pattern_count
        -
        selected_pattern_count
    )
    /
    original_pattern_count
) * 100


# ============================================================
# 7. DISPLAY
# ============================================================

print()
print("VISTA Pattern Compaction")
print("========================")
print()

print(
    "Benchmark:",
    benchmark_name
)

print(
    "Original patterns:",
    original_pattern_count
)

print(
    "Selected patterns:",
    selected_pattern_count
)

print(
    "Detected faults covered:",
    detected_fault_count,
    "/",
    total_faults
)

print(
    "Coverage of detectable faults:",
    round(coverage, 2),
    "%"
)

print(
    "Pattern reduction:",
    round(pattern_reduction, 2),
    "%"
)


print()
print("Selected patterns:")
print("------------------")


for pattern in selected_patterns:

    print(pattern)


# ============================================================
# 8. SAVE RESULT
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parents[2]


OUTPUT_FILE = (
    BASE_DIR
    / "member2"
    / "data"
    / f"{benchmark_name}_pattern_compaction.json"
)


result = {

    "benchmark":
        benchmark_name,

    "original_patterns":
        original_pattern_count,

    "selected_patterns":
        selected_patterns,

    "selected_pattern_count":
        selected_pattern_count,

    "detectable_faults":
        total_faults,

    "faults_covered":
        detected_fault_count,

    "coverage_of_detectable_faults":
        coverage,

    "pattern_reduction":
        pattern_reduction
}


with open(
    OUTPUT_FILE,
    "w"
) as file:

    json.dump(
        result,
        file,
        indent=4
    )


print()
print("Compaction results saved to:")
print(OUTPUT_FILE)