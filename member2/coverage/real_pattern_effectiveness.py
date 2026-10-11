import json

with open("../data/real_simulation_results.json", "r") as file:
    results = json.load(file)

patterns = {}

for result in results:

    pattern_id = result["pattern_id"]

    if pattern_id not in patterns:
        patterns[pattern_id] = {
            "detected_faults": [],
            "detection_count": 0
        }

    if result["detected"]:
        patterns[pattern_id]["detected_faults"].append(
            result["fault_id"]
        )

        patterns[pattern_id]["detection_count"] += 1


pattern_results = []

for pattern_id, info in patterns.items():

    pattern_results.append({
        "pattern_id": pattern_id,
        "detected_faults": info["detected_faults"],
        "detection_count": info["detection_count"]
    })


pattern_results.sort(
    key=lambda x: x["detection_count"],
    reverse=True
)


for pattern in pattern_results:

    print(
        "Pattern:", pattern["pattern_id"],
        "| Detected faults:", pattern["detected_faults"],
        "| Count:", pattern["detection_count"]
    )


with open("../data/real_pattern_effectiveness.json", "w") as file:

    json.dump(
        pattern_results,
        file,
        indent=4
    )

print()
print("Pattern effectiveness saved to:")
print("../data/real_pattern_effectiveness.json")