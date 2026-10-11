import json


RESULTS_FILE = "../data/c17_simulation_results.json"
COMPACTION_FILE = "../data/c17_pattern_compaction.json"


with open(RESULTS_FILE, "r") as file:
    results = json.load(file)

with open(COMPACTION_FILE, "r") as file:
    compaction = json.load(file)


selected_patterns = set(
    compaction["selected_patterns"]
)


all_faults = set()
covered_faults = set()


for fault in results:

    fault_id = fault["fault_id"]

    all_faults.add(fault_id)

    detected_patterns = set(
        fault.get("detected_patterns", [])
    )

    if detected_patterns & selected_patterns:
        covered_faults.add(fault_id)


uncovered_faults = all_faults - covered_faults


coverage = (
    len(covered_faults) /
    len(all_faults)
) * 100


print("C17 Compaction Verification")
print("============================")

print(
    "Original patterns:",
    compaction["original_patterns"]
)

print(
    "Selected patterns:",
    len(selected_patterns)
)

print(
    "Selected:",
    sorted(selected_patterns)
)

print(
    "Faults covered:",
    len(covered_faults),
    "/",
    len(all_faults)
)

print(
    "Verified coverage:",
    round(coverage, 2),
    "%"
)

print(
    "Uncovered faults:",
    len(uncovered_faults)
)


if uncovered_faults:

    print()
    print("ERROR - Uncovered faults:")

    for fault in sorted(uncovered_faults):
        print(fault)

else:

    print()
    print("PASS - All faults are covered by the selected patterns.")