
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = BASE_DIR / "data" / "c499_simulation_records.json"
OUTPUT_FILE = BASE_DIR / "data" / "c499_compaction_results.json"


def main():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    # Build the set of detectable faults for each pattern.
    pattern_faults = {}
    all_detectable_faults = set()

    for record in records:
        pattern = record["pattern_id"]
        fault = record["fault_id"]

        pattern_faults.setdefault(pattern, set())

        if record["detected"]:
            pattern_faults[pattern].add(fault)
            all_detectable_faults.add(fault)

    # Greedy set-cover compaction.
    uncovered = set(all_detectable_faults)
    selected_patterns = []

    while uncovered:
        best_pattern = None
        best_new_faults = set()

        for pattern, faults in pattern_faults.items():
            if pattern in selected_patterns:
                continue

            new_faults = faults & uncovered

            if len(new_faults) > len(best_new_faults):
                best_pattern = pattern
                best_new_faults = new_faults

        if best_pattern is None or not best_new_faults:
            break

        selected_patterns.append(best_pattern)
        uncovered -= best_new_faults

    # Independently recompute coverage from the selected patterns.
    verified_faults = set()

    for pattern in selected_patterns:
        verified_faults.update(pattern_faults[pattern])

    coverage_preserved = verified_faults == all_detectable_faults
    original_count = len(pattern_faults)
    selected_count = len(selected_patterns)
    reduction_pct = (
        100 * (original_count - selected_count) / original_count
        if original_count else 0
    )

    result = {
        "circuit": "c499",
        "method": "greedy_set_cover",
        "original_patterns": original_count,
        "selected_patterns": selected_patterns,
        "selected_pattern_count": selected_count,
        "detectable_faults": len(all_detectable_faults),
        "verified_covered_faults": len(verified_faults),
        "uncovered_faults": sorted(uncovered),
        "coverage_preserved": coverage_preserved,
        "pattern_reduction_pct": round(reduction_pct, 2),
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)

    print("C499 Pattern Compaction")
    print("-----------------------")
    print("Original patterns:", original_count)
    print("Selected patterns:", selected_count)
    print("Detectable faults:", len(all_detectable_faults))
    print("Verified covered faults:", len(verified_faults))
    print("Pattern reduction:", f"{reduction_pct:.2f}%")
    print("Coverage preserved:", coverage_preserved)
    print("Uncovered faults:", len(uncovered))
    print("Results saved to:", OUTPUT_FILE)

    if not coverage_preserved:
        raise SystemExit("FAIL: detectable-fault coverage was not preserved.")

    print("PASS: all detectable faults remain covered.")


if __name__ == "__main__":
    main()
