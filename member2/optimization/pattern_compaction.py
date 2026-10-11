import json

with open("../data/simulation_results.json", "r") as file:
    results = json.load(file)

pattern_faults = {}

for result in results:
    pattern = result["pattern_id"]
    fault = result["fault_id"]

    if result["detected"]:
        if pattern not in pattern_faults:
            pattern_faults[pattern] = set()

        pattern_faults[pattern].add(fault)

covered_faults = set()
selected_patterns = []

while True:
    best_pattern = None
    best_new_faults = set()

    for pattern, faults in pattern_faults.items():
        new_faults = faults - covered_faults

        if len(new_faults) > len(best_new_faults):
            best_pattern = pattern
            best_new_faults = new_faults

    if best_pattern is None:
        break

    selected_patterns.append(best_pattern)
    covered_faults.update(best_new_faults)

print("Selected patterns:", selected_patterns)
print("Faults covered:", covered_faults)