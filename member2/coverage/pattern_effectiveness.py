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

for pattern, faults in pattern_faults.items():
    print(pattern, "detects", len(faults), "faults")