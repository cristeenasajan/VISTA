
import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "member2" / "data"
BENCHMARK = PROJECT_ROOT / "benchmarks" / "c499.bench"

MATRIX_FILE = DATA_DIR / "c499_detection_matrix_recheck.json"
ATPG_FILE = DATA_DIR / "c499_atpg_report.json"
REDUCED_REPORT = DATA_DIR / "c499_reduced_75_patterns.json"
FRESH_MATRIX = DATA_DIR / "c499_reduced_75_matrix.json"

RECORDS_FILE = DATA_DIR / "c499_simulation_records.json"
COMPACTION_FILE = DATA_DIR / "c499_compaction_results.json"

ADAPTER = PROJECT_ROOT / "member2" / "optimization" / "member1_matrix_adapter.py"
COMPACTOR = PROJECT_ROOT / "member2" / "optimization" / "c499_pattern_compaction.py"
REPORT_CREATOR = PROJECT_ROOT / "member2" / "optimization" / "create_c499_reduced_report.py"

PYTHON = Path(sys.executable)
IVERILOG_BIN = Path(
    os.environ.get("MSYS2_UCRT64_BIN", r"C:\msys64\ucrt64\bin")
)


def run_command(command, cwd, env=None):
    """Run a command and stop immediately if it fails."""
    command = [str(item) for item in command]
    print("\n>", subprocess.list2cmdline(command), flush=True)
    subprocess.run(command, cwd=str(cwd), env=env, check=True)


def run_python(script, *args):
    run_command([PYTHON, script, *args], PROJECT_ROOT)


def verify_compaction():
    """Verify selected patterns against the original detection matrix."""
    matrix = json.loads(MATRIX_FILE.read_text(encoding="utf-8"))
    result = json.loads(COMPACTION_FILE.read_text(encoding="utf-8"))

    selected = {int(item) for item in result["selected_patterns"]}
    detectable = {
        fault["id"]: {int(p) for p in fault.get("detecting_patterns", [])}
        for fault in matrix["faults"]
        if fault.get("detected", False)
    }

    covered = {
        fault_id
        for fault_id, pattern_ids in detectable.items()
        if pattern_ids & selected
    }

    if len(selected) != 75:
        raise RuntimeError(f"Expected 75 selected patterns; got {len(selected)}")
    if len(detectable) != 750 or covered != set(detectable):
        raise RuntimeError("Compaction did not preserve all detectable faults")
    if result.get("coverage_preserved") is not True:
        raise RuntimeError("Compaction report does not confirm preserved coverage")

    print("\nPASS: Original-matrix compaction check — 750/750 detectable faults retained.")


def verify_fresh_matrix():
    """Validate the fresh matrix against the original detectable fault set."""
    original = json.loads(MATRIX_FILE.read_text(encoding="utf-8"))
    fresh = json.loads(FRESH_MATRIX.read_text(encoding="utf-8"))

    original_detectable = {
        fault["id"] for fault in original["faults"] if fault.get("detected", False)
    }
    fresh_detected = {
        fault["id"] for fault in fresh["faults"] if fault.get("detected", False)
    }

    if len(fresh["patterns"]) != 75:
        raise RuntimeError("Fresh matrix does not contain exactly 75 patterns")
    if len(fresh["faults"]) != 758:
        raise RuntimeError("Fresh matrix does not contain 758 faults")
    if not original_detectable.issubset(fresh_detected):
        missing = sorted(original_detectable - fresh_detected)
        raise RuntimeError(f"Fresh matrix lost detectable faults: {missing}")
    if len(fresh_detected) != 750:
        raise RuntimeError(f"Expected 750 detected faults; got {len(fresh_detected)}")

    print("PASS: Fresh matrix — all 750 originally detectable faults retained.")
    print("Fresh total fault coverage: 750/758 = 98.94%.")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the VISTA C499 integration workflow."
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run the slower independent reference simulator.",
    )
    args = parser.parse_args()

    required_files = [
        BENCHMARK, MATRIX_FILE, ATPG_FILE, ADAPTER,
        COMPACTOR, REPORT_CREATOR, PYTHON,
    ]
    missing = [path for path in required_files if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing required files:\n" + "\n".join(str(path) for path in missing)
        )

    print("VISTA C499 integration workflow", flush=True)

    # 1. Convert the original matrix into Member 2's record format.
    run_python(ADAPTER, str(MATRIX_FILE), str(RECORDS_FILE))

    # 2. Compact the patterns.
    run_python(COMPACTOR)

    # 3. Check compaction against the original detection mappings.
    verify_compaction()

    # 4. Create the reduced ATPG report.
    run_python(REPORT_CREATOR)

    # 5. Regenerate the detection matrix using the local engine.
    env = os.environ.copy()
    env["PATH"] = str(IVERILOG_BIN) + os.pathsep + env.get("PATH", "")

    matrix_command = [
        PYTHON, "-m", "vista.matrix",
        str(BENCHMARK),
        "--model", "stuck-at",
        "--patterns", str(REDUCED_REPORT),
        "--json", str(FRESH_MATRIX),
    ]

    if args.verify:
        matrix_command.append("--verify")
        print("\nIndependent reference verification: ENABLED", flush=True)
    else:
        print("\nIndependent reference verification: SKIPPED", flush=True)

    run_command(matrix_command, PROJECT_ROOT, env)

    # 6. Verify the regenerated matrix.
    verify_fresh_matrix()

    print("\nSUCCESS: C499 workflow and coverage checks passed.", flush=True)
    if args.verify:
        print("The matrix command completed with --verify.", flush=True)
    else:
        print("Note: independent reference verification was not run.", flush=True)


if __name__ == "__main__":
    main()
