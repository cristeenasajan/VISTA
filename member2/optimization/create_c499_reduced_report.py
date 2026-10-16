
import json
from pathlib import Path


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "member2" / "data"

ATPG_FILE = DATA_DIR / "c499_atpg_report.json"
COMPACTION_FILE = DATA_DIR / "c499_compaction_results.json"
OUTPUT_FILE = DATA_DIR / "c499_reduced_75_patterns.json"


# --------------------------------------------------
# JSON helpers
# --------------------------------------------------

def load_json(path):
    """Load a JSON file and return its contents."""

    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    """Write JSON with readable formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")


# --------------------------------------------------
# Pattern ID helpers
# --------------------------------------------------

def get_pattern_id(pattern):
    """Extract the pattern identifier from an ATPG pattern."""

    if not isinstance(pattern, dict):
        raise ValueError(
            f"Expected a pattern object, got: {pattern!r}"
        )

    # The supplied C499 ATPG report uses "index".
    for key in ("index", "id", "pattern_id", "pattern"):
        if key in pattern:
            return pattern[key]

    raise ValueError(
        f"Pattern record has no recognized identifier: {pattern!r}"
    )


def normalize_id(value):
    """Normalize integer-like IDs for comparison."""

    if isinstance(value, bool):
        raise ValueError("Boolean values are not valid pattern IDs.")

    if isinstance(value, int):
        return value

    if isinstance(value, str):
        value = value.strip()

        try:
            return int(value)
        except ValueError:
            return value

    return value


# --------------------------------------------------
# Main workflow
# --------------------------------------------------

def main():
    print("VISTA C499 Reduced ATPG Report Creator")
    print("--------------------------------------")

    atpg = load_json(ATPG_FILE)
    compaction = load_json(COMPACTION_FILE)

    if not isinstance(atpg, dict):
        raise ValueError("ATPG report must be a JSON object.")

    if not isinstance(compaction, dict):
        raise ValueError("Compaction report must be a JSON object.")

    original_patterns = atpg.get("patterns")
    selected_list = compaction.get("selected_patterns")

    if not isinstance(original_patterns, list):
        raise ValueError("ATPG report must contain a patterns list.")

    if not isinstance(selected_list, list):
        raise ValueError(
            "Compaction report must contain selected_patterns."
        )

    # Normalize the selected IDs.
    selected_ids = {
        normalize_id(pattern_id)
        for pattern_id in selected_list
    }

    if len(selected_ids) != 75:
        raise RuntimeError(
            f"Expected 75 unique selected pattern IDs; "
            f"found {len(selected_ids)}."
        )

    # Build a mapping from pattern ID to original record.
    pattern_by_id = {}

    for pattern in original_patterns:
        pattern_id = normalize_id(get_pattern_id(pattern))

        if pattern_id in pattern_by_id:
            raise RuntimeError(
                f"Duplicate pattern ID in ATPG report: {pattern_id!r}"
            )

        pattern_by_id[pattern_id] = pattern

    # Preserve the original ATPG ordering for the selected patterns.
    missing_ids = selected_ids - set(pattern_by_id)

    if missing_ids:
        raise RuntimeError(
            "Selected pattern IDs were not found in the ATPG report: "
            f"{sorted(missing_ids, key=str)}"
        )

    reduced_patterns = [
        pattern
        for pattern in original_patterns
        if normalize_id(get_pattern_id(pattern)) in selected_ids
    ]

    if len(reduced_patterns) != 75:
        raise RuntimeError(
            f"Expected exactly 75 reduced patterns; "
            f"found {len(reduced_patterns)}."
        )

    # Preserve the original metadata and replace only the pattern list.
    reduced_report = dict(atpg)
    reduced_report["patterns"] = reduced_patterns

    # Update summary counts only if these fields already exist.
    if isinstance(reduced_report.get("summary"), dict):
        reduced_report["summary"] = dict(reduced_report["summary"])

        for key in ("patterns", "pattern_count", "total_patterns"):
            if key in reduced_report["summary"]:
                reduced_report["summary"][key] = 75

    # Write and read back the generated report.
    save_json(OUTPUT_FILE, reduced_report)
    saved_report = load_json(OUTPUT_FILE)

    if len(saved_report.get("patterns", [])) != 75:
        raise RuntimeError(
            "Output validation failed: expected exactly 75 patterns."
        )

    print(f"Original patterns: {len(original_patterns)}")
    print(f"Selected patterns: {len(selected_ids)}")
    print(f"Reduced patterns:  {len(reduced_patterns)}")
    print(f"Output: {OUTPUT_FILE}")
    print("PASS: Reduced ATPG report created and validated.")


if __name__ == "__main__":
    main()
