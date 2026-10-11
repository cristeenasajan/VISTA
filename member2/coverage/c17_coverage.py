import json


INPUT_FILE = "../data/c17_simulation_results.json"


with open(INPUT_FILE, "r") as file:
    results = json.load(file)


total_faults = len(results)

detected_faults = 0

undetected_faults = []


for fault in results:

    if fault.get("detection_count", 0) > 0:
        detected_faults += 1
    else:
        undetected_faults.append(fault["fault_id"])


coverage = (
    detected_faults /
    total_faults
) * 100


print("C17 Fault Coverage")
print("==================")

print("Total faults:", total_faults)
print("Detected faults:", detected_faults)
print("Undetected faults:", len(undetected_faults))
print("Fault coverage:", round(coverage, 2), "%")


if undetected_faults:

    print()
    print("Undetected faults:")

    for fault_id in undetected_faults:
        print(fault_id)