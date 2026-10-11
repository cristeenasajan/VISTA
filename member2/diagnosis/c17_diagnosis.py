import json

INPUT_FILE = "../data/c17_simulation_results.json"
OUTPUT_FILE = "../data/c17_fault_diagnosis.json"

with open(INPUT_FILE, "r") as file:
    results = json.load(file)

diagnosis = []

for fault in results:

    detection_count = fault.get("detection_count", 0)

    if detection_count == 0:
        difficulty = "Hard"
    elif detection_count <= 8:
        difficulty = "Medium"
    else:
        difficulty = "Easy"

    diagnosis.append({
        "fault_id": fault["fault_id"],
        "net": fault["net"],
        "fault_type": fault["fault_type"],
        "detected_patterns": fault.get("detected_patterns", []),
        "detection_count": detection_count,
        "difficulty": difficulty
    })

print("C17 Fault Diagnosis")
print("===================")

for fault in diagnosis:

    print(
        fault["fault_id"],
        "|",
        fault["net"],
        "|",
        fault["fault_type"],
        "| Detected:",
        fault["detection_count"],
        "| Difficulty:",
        fault["difficulty"]
    )

with open(OUTPUT_FILE, "w") as file:
    json.dump(diagnosis, file, indent=4)

print()
print("Diagnosis saved to:")
print(OUTPUT_FILE)