
import argparse
import json
from pathlib import Path


def convert_detection_matrix(input_path, output_path):
    input_path = Path(input_path)
    output_path = Path(output_path)

    with input_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    # Validate the report before converting it.
    if report.get("schema_version") != "1.1":
        raise ValueError("Expected a VISTA schema 1.1 report.")

    if report.get("document") != "fault_sim_report":
        raise ValueError("Input is not a fault_sim_report.")

    patterns = report.get("patterns", [])
    faults = report.get("faults", [])

    if not patterns or not faults:
        raise ValueError("Report contains no patterns or faults.")

    # Build the output records expected by the existing compaction script.
    # A record is created for each pattern-fault pair.
    results = []
    pattern_ids = {pattern["index"] for pattern in patterns}

    for fault in faults:
        fault_id = fault["id"]
        detecting_patterns = set(fault.get("detecting_patterns", []))

        # Validate references to patterns.
        unknown_patterns = detecting_patterns - pattern_ids
        if unknown_patterns:
            raise ValueError(
                f"Fault {fault_id} references unknown patterns: "
                f"{sorted(unknown_patterns)}"
            )

        for pattern in patterns:
            pattern_id = pattern["index"]

            results.append({
                "pattern_id": str(pattern_id),
                "fault_id": fault_id,
                "detected": pattern_id in detecting_patterns,
            })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    detected_faults = sum(
        1 for fault in faults if fault.get("detected", False)
    )
    mapped_faults = sum(
        1
        for fault in faults
        if fault.get("detected", False)
        and fault.get("detecting_patterns")
    )

    print("VISTA Member 1 Detection-Matrix Adapter")
    print("---------------------------------------")
    print("Circuit:", report.get("circuit"))
    print("Patterns:", len(patterns))
    print("Fault records:", len(faults))
    print("Detected faults:", detected_faults)
    print("Detected faults with pattern mappings:", mapped_faults)
    print("Output records:", len(results))
    print("Output file:", output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Convert a VISTA schema 1.1 detection matrix "
                    "to Member 2 simulation-record format."
    )
    parser.add_argument("input", help="Input detection-matrix JSON")
    parser.add_argument("output", help="Output simulation-record JSON")
    args = parser.parse_args()

    convert_detection_matrix(args.input, args.output)


if __name__ == "__main__":
    main()
