import json
import sys
from pathlib import Path


# ============================================================
# 1. CHECK ARGUMENT
# ============================================================

if len(sys.argv) < 2:
    print("Usage:")
    print("python fault_diagnosis.py <simulation_results.json>")
    sys.exit(1)


INPUT_FILE = Path(sys.argv[1])


# ============================================================
# 2. READ RESULTS
# ============================================================

with open(INPUT_FILE, "r") as file:
    results = json.load(file)


# ============================================================
# 3. DETERMINE BENCHMARK NAME
# ============================================================

benchmark_name = INPUT_FILE.stem.replace(
    "_simulation_results",
    ""
)


# ============================================================
# 4. DIAGNOSE FAULTS
# ============================================================

diagnosis = []


for result in results:

    fault_id = result["fault_id"]
    net = result["net"]
    fault_type = result["fault_type"]

    detected_patterns = result.get(
        "detected_patterns",
        []
    )

    detection_count = len(
        detected_patterns
    )


    # --------------------------------------------------------
    # Difficulty classification
    # --------------------------------------------------------

    if detection_count == 0:

        difficulty = "Hard"

    elif detection_count <= 8:

        difficulty = "Medium"

    else:

        difficulty = "Easy"


    # --------------------------------------------------------
    # Diagnosis record
    # --------------------------------------------------------

    diagnosis.append({

        "fault_id":
            fault_id,

        "net":
            net,

        "fault_type":
            fault_type,

        "detected_by":
            detected_patterns,

        "detection_count":
            detection_count,

        "difficulty":
            difficulty
    })


# ============================================================
# 5. SORT HARDEST FIRST
# ============================================================

diagnosis.sort(
    key=lambda x: x["detection_count"]
)


# ============================================================
# 6. OUTPUT FILE
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    BASE_DIR
    / "member2"
    / "data"
    / f"{benchmark_name}_fault_diagnosis.json"
)


# ============================================================
# 7. SAVE
# ============================================================

with open(
    OUTPUT_FILE,
    "w"
) as file:

    json.dump(
        diagnosis,
        file,
        indent=4
    )


# ============================================================
# 8. SUMMARY
# ============================================================

hard = sum(
    1
    for x in diagnosis
    if x["difficulty"] == "Hard"
)

medium = sum(
    1
    for x in diagnosis
    if x["difficulty"] == "Medium"
)

easy = sum(
    1
    for x in diagnosis
    if x["difficulty"] == "Easy"
)


print()
print("VISTA Fault Diagnosis")
print("=====================")
print()
print("Benchmark:", benchmark_name)
print("Total faults:", len(diagnosis))
print("Hard:", hard)
print("Medium:", medium)
print("Easy:", easy)
print()


print("Hardest faults:")
print("----------------")


for fault in diagnosis[:10]:

    print(
        fault["fault_id"],
        "->",
        fault["net"],
        fault["fault_type"],
        "| Detected:",
        fault["detection_count"],
        "|",
        fault["difficulty"]
    )


print()
print("Diagnosis saved to:")
print(OUTPUT_FILE)