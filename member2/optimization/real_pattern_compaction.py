import json
import sys
from pathlib import Path


# ============================================================
# 1. CHECK ARGUMENTS
# ============================================================

if len(sys.argv) < 2:

    print("Usage:")
    print(
        "python real_pattern_compaction.py "
        "<simulation_results.json>"
    )

    sys.exit(1)


SIMULATION_FILE = Path(
    sys.argv[1]
)


# ============================================================
# 2. READ SIMULATION RESULTS
# ============================================================

with open(
    SIMULATION_FILE,
    "r"
) as file:

    results = json.load(file)


# ============================================================
# 3. DETERMINE BENCHMARK NAME
# ============================================================

benchmark_name = (
    SIMULATION_FILE.stem
    .replace(
        "_simulation_results",
        ""
    )
)


# ============================================================
# 4. BUILD PATTERN -> FAULTS MAP
# ============================================================

pattern_faults = {}


all_faults = set()


for result in results:

    # Ignore failed simulations.
    if "error" in result:
        continue


    fault_id = result["fault_id"]

    all_faults.add(
        fault_id
    )


    detected_patterns = result.get(
        "detected_patterns",
        []
    )


    for pattern in detected_patterns:

        if pattern not in pattern_faults:

            pattern_faults[pattern] = set()


        pattern_faults[pattern].add(
            fault_id
        )


# ============================================================
# 5. DETERMINE DETECTABLE FAULTS
# ============================================================

detectable_faults = set()


for pattern in pattern_faults:

    detectable_faults.update(
        pattern_faults[pattern]
    )


# ============================================================
# 6. GREEDY SET COVER
# ============================================================

remaining_faults = set(
    detectable_faults
)


selected_patterns = []


while remaining_faults:

    best_pattern = None

    best_faults = set()


    for pattern, faults in pattern_faults.items():

        newly_detected = (
            faults
            & remaining_faults
        )


        if len(newly_detected) > len(best_faults):

            best_pattern = pattern

            best_faults = newly_detected


    # No pattern can cover any remaining fault.
    if best_pattern is None:

        break


    selected_patterns.append(
        best_pattern
    )


    remaining_faults -= best_faults


# ============================================================
# 7. CALCULATE RESULTS
# ============================================================

original_pattern_count = len(
    pattern_faults
)


selected_pattern_count = len(
    selected_patterns
)


covered_faults = (
    detectable_faults
    - remaining_faults
)


if original_pattern_count > 0:

    pattern_reduction = (
        (
            original_pattern_count
            - selected_pattern_count
        )
        /
        original_pattern_count
    ) * 100

else:

    pattern_reduction = 0.0


if len(detectable_faults) > 0:

    compaction_coverage = (
        len(covered_faults)
        /
        len(detectable_faults)
    ) * 100

else:

    compaction_coverage = 0.0


# ============================================================
# 8. DISPLAY SUMMARY
# ============================================================

print()
print("VISTA Pattern Compaction")
print("========================")

print(
    "Benchmark:",
    benchmark_name
)

print(
    "Total faults:",
    len(all_faults)
)

print(
    "Detectable faults:",
    len(detectable_faults)
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
    "Patterns removed:",
    original_pattern_count
    - selected_pattern_count
)

print(
    "Pattern reduction:",
    f"{pattern_reduction:.2f}%"
)

print(
    "Compaction coverage:",
    f"{compaction_coverage:.2f}%"
)


# ============================================================
# 9. SELECTED PATTERNS
# ============================================================

print()
print("Selected patterns:")
print("------------------")


for pattern in selected_patterns:

    print(
        pattern,
        "detects",
        len(
            pattern_faults[pattern]
        ),
        "faults"
    )


# ============================================================
# 10. VERIFY COVERAGE
# ============================================================

print()
print("Verification")
print("------------")

if len(remaining_faults) == 0:

    print(
        "PASS - All detectable faults "
        "are covered."
    )

else:

    print(
        "WARNING - Some detectable faults "
        "remain uncovered."
    )

    print(
        "Uncovered faults:",
        sorted(
            remaining_faults
        )
    )


# ============================================================
# 11. SAVE RESULTS
# ============================================================

output_file = (
    SIMULATION_FILE.parent
    /
    f"{benchmark_name}_pattern_compaction.json"
)


compaction_result = {

    "benchmark":
        benchmark_name,

    "total_faults":
        len(all_faults),

    "detectable_faults":
        len(detectable_faults),

    "original_pattern_count":
        original_pattern_count,

    "selected_pattern_count":
        selected_pattern_count,

    "pattern_reduction_percent":
        pattern_reduction,

    "compaction_coverage_percent":
        compaction_coverage,

    "selected_patterns":
        selected_patterns,

    "covered_faults":
        sorted(
            covered_faults
        ),

    "uncovered_detectable_faults":
        sorted(
            remaining_faults
        )
}


with open(
    output_file,
    "w"
) as file:

    json.dump(
        compaction_result,
        file,
        indent=4
    )


print()
print(
    "Compaction results saved to:"
)

print(
    output_file
)