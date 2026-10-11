import json

with open("../data/real_simulation_results.json", "r") as file:
    results = json.load(file)

faults = {}

for result in results:

    fault_id = result["fault_id"]

    if fault_id not in faults:
        faults[fault_id] = {
            "detected_patterns": [],
            "detection_count": 0
        }

    if result["detected"]:
        faults[fault_id]["detected_patterns"].append(
            result["pattern_id"]
        )

        faults[fault_id]["detection_count"] += 1


diagnosis = []

for fault_id, info in faults.items():

    count = info["detection_count"]

    if count == 0:
        difficulty = "Hard"
    elif count == 1:
        difficulty = "Medium"
    else:
        difficulty = "Easy"

    diagnosis.append({
        "fault_id": fault_id,
        "detected_patterns": info["detected_patterns"],
        "detection_count": count,
        "difficulty": difficulty
    })


for fault in diagnosis:

    print(
        "Fault:", fault["fault_id"],
        "| Detected by:", fault["detected_patterns"],
        "| Count:", fault["detection_count"],
        "| Difficulty:", fault["difficulty"]
    )


with open("../data/real_fault_diagnosis.json", "w") as file:

    json.dump(
        diagnosis,
        file,
        indent=4
    )

print()
print("Real diagnosis saved to:")
print("../data/real_fault_diagnosis.json")