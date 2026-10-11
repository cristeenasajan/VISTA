import json

with open("../data/fault_diagnosis.json", "r") as file:
    diagnosis = json.load(file)

total_patterns = 3

dataset = []

for fault in diagnosis:

    detection_count = fault["detection_count"]

    detection_ratio = detection_count / total_patterns

    dataset.append({
        "fault_id": fault["fault_id"],
        "detection_count": detection_count,
        "pattern_count": total_patterns,
        "detection_ratio": detection_ratio,
        "difficulty": fault["difficulty"]
    })

with open("../data/ml_dataset.json", "w") as file:
    json.dump(dataset, file, indent=4)

print("ML dataset created.")
print("Samples:", len(dataset))