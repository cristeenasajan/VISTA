import json
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "member2" / "data"

SIMULATION_FILE = (
    DATA_DIR / "c432_simulation_results.json"
)

COMPACTION_FILE = (
    DATA_DIR / "c432_pattern_compaction.json"
)


# ============================================================
# LOAD DATA
# ============================================================

with open(SIMULATION_FILE, "r") as file:
    simulation = json.load(file)


with open(COMPACTION_FILE, "r") as file:
    compaction = json.load(file)


# ============================================================
# SELECTED PATTERNS
# ============================================================

selected_patterns = set(
    compaction["selected_patterns"]
)


# ============================================================
# BUILD FAULT -> DETECTED PATTERNS
# ============================================================

fault_patterns = {}

for result in simulation:

    fault_id = result["fault_id"]

    detected_patterns = result.get(
        "detected_patterns",
        []
    )

    fault_patterns[fault_id] = set(
        detected_patterns
    )


# ============================================================
# DETECTABLE FAULTS
# ============================================================

detectable_faults = set()

for fault_id, patterns in fault_patterns.items():

    if patterns:
        detectable_faults.add(fault_id)


# ============================================================
# CHECK SELECTED PATTERNS
# ============================================================

covered_faults = set()


for fault_id, patterns in fault_patterns.items():

    if patterns & selected_patterns:

        covered_faults.add(
            fault_id
        )


# ============================================================
# STATISTICS
# ============================================================

original_patterns = 1024

selected_count = len(
    selected_patterns
)

detectable_count = len(
    detectable_faults
)

covered_count = len(
    covered_faults
)


if detectable_count > 0:

    coverage = (
        covered_count /
        detectable_count
    ) * 100

else:

    coverage = 0


pattern_reduction = (
    (
        original_patterns -
        selected_count
    )
    /
    original_patterns
) * 100


uncovered_faults = (
    detectable_faults -
    covered_faults
)


# ============================================================
# DISPLAY
# ============================================================

print()
print("VISTA C432 Compaction Verification")
print("===================================")
print()

print(
    "Original patterns:",
    original_patterns
)

print(
    "Selected patterns:",
    selected_count
)

print(
    "Detectable faults:",
    detectable_count
)

print(
    "Faults covered:",
    covered_count
)

print(
    "Verified coverage:",
    round(
        coverage,
        2
    ),
    "%"
)

print(
    "Pattern reduction:",
    round(
        pattern_reduction,
        2
    ),
    "%"
)

print()

print(
    "Uncovered detectable faults:",
    len(
        uncovered_faults
    )
)


# ============================================================
# FINAL VERDICT
# ============================================================

if not uncovered_faults:

    print()
    print(
        "PASS - All detectable faults are "
        "covered by the selected patterns."
    )

else:

    print()
    print(
        "WARNING - Some detectable faults "
        "are not covered."
    )

    print()
    print("Uncovered faults:")

    for fault in sorted(
        uncovered_faults
    ):

        print(fault)