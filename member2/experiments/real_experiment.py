import json


# Load real simulation results
with open("../data/real_simulation_results.json", "r") as file:
    simulation = json.load(file)


# Load compaction results
with open("../data/real_pattern_compaction.json", "r") as file:
    compaction = json.load(file)


# Fault coverage
all_faults = set()
detected_faults = set()

for result in simulation:

    fault_id = result["fault_id"]

    all_faults.add(fault_id)

    if result["detected"]:
        detected_faults.add(fault_id)


total_faults = len(all_faults)
detected_count = len(detected_faults)

if total_faults > 0:
    coverage = detected_count / total_faults * 100
else:
    coverage = 0


# Pattern statistics
original_patterns = compaction["original_pattern_count"]
selected_patterns = compaction["selected_pattern_count"]

if original_patterns > 0:

    reduction = (
        (original_patterns - selected_patterns)
        / original_patterns
    ) * 100

else:
    reduction = 0


# Print report
print("================================")
print("       VISTA REAL EXPERIMENT")
print("================================")

print()
print("Fault Statistics")
print("----------------")
print("Total faults:", total_faults)
print("Detected faults:", detected_count)
print("Fault coverage:", coverage, "%")

print()
print("Pattern Statistics")
print("------------------")
print("Original patterns:", original_patterns)
print("Selected patterns:", selected_patterns)
print("Pattern reduction:", reduction, "%")


# Save report
report = {
    "total_faults": total_faults,
    "detected_faults": detected_count,
    "fault_coverage_percent": coverage,
    "original_patterns": original_patterns,
    "selected_patterns": selected_patterns,
    "pattern_reduction_percent": reduction
}


with open("../data/real_experiment_report.json", "w") as file:

    json.dump(
        report,
        file,
        indent=4
    )


print()
print("Experiment report saved to:")
print("../data/real_experiment_report.json")