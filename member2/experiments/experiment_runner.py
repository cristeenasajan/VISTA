import json

with open("../data/faults.json", "r") as file:
    faults = json.load(file)

with open("../data/simulation_results.json", "r") as file:
    results = json.load(file)

total_faults = len(faults)

detected_faults = set()

for result in results:
    if result["detected"]:
        detected_faults.add(result["fault_id"])

detected_count = len(detected_faults)

fault_coverage = (detected_count / total_faults) * 100

total_patterns = len(
    set(result["pattern_id"] for result in results)
)

print("===== VISTA EXPERIMENT =====")
print("Total faults:", total_faults)
print("Detected faults:", detected_count)
print("Fault coverage:", fault_coverage, "%")
print("Total patterns:", total_patterns)