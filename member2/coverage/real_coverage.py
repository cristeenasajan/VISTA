import json

with open("../data/real_simulation_results.json", "r") as file:
    results = json.load(file)

total_faults = set()
detected_faults = set()

for result in results:

    fault_id = result["fault_id"]

    total_faults.add(fault_id)

    if result["detected"]:
        detected_faults.add(fault_id)

total = len(total_faults)
detected = len(detected_faults)

if total > 0:
    coverage = (detected / total) * 100
else:
    coverage = 0

print("Real Fault Simulation Coverage")
print("-------------------------------")
print("Total faults:", total)
print("Detected faults:", detected)
print("Fault coverage:", coverage, "%")