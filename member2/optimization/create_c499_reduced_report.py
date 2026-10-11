
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MEMBER1_ROOT = PROJECT_ROOT.parent / "VISTA_member1"

ATPG_FILE = MEMBER1_ROOT / "c499_atpg_report.json"
COMPACTION_FILE = (
    PROJECT_ROOT / "member2" / "data" / "c499_compaction_results.json"
)
OUTPUT_FILE = MEMBER1_ROOT / "c499_reduced_75_patterns.json"


def main():
    with ATPG_FILE.open("r", encoding="utf-8") as file:
        atpg = json.load(file)

    with COMPACTION_FILE.open("r", encoding="utf-8") as file:
        compaction = json.load(file)

    selected_ids = {
        int(pattern_id)
        for pattern_id in compaction["selected_patterns"]
    }

    original_patterns = {
        pattern["index"]: pattern
        for pattern in atpg["patterns"]
    }

    missing = selected_ids - set(original_patterns)
    if missing:
        raise ValueError(f"Selected IDs missing from ATPG report: {sorted(missing)}")

    # Preserve the selected patterns' original entries and their bit vectors.
    reduced = dict(atpg)
    reduced["patterns"] = [
        original_patterns[index]
        for index in sorted(selected_ids)
    ]

    # Preserve the original report metadata, but update the pattern count
    # in the copied summary if that field exists.
    if isinstance(reduced.get("summary"), dict):
        for key in ("patterns", "pattern_count", "total_patterns"):
            if key in reduced["summary"]:
                reduced["summary"][key] = len(selected_ids)

    OUTPUT_FILE.write_text(
        json.dumps(reduced, indent=2),
        encoding="utf-8",
    )

    print("Reduced C499 ATPG report created")
    print("Original patterns:", len(atpg["patterns"]))
    print("Selected patterns:", len(reduced["patterns"]))
    print("Unique selected IDs:", len(selected_ids))
    print("Pattern width:", len(reduced["patterns"][0]["bits"]))
    print("Output:", OUTPUT_FILE)

    if len(reduced["patterns"]) != 75:
        raise RuntimeError("Expected exactly 75 selected patterns.")


if __name__ == "__main__":
    main()
