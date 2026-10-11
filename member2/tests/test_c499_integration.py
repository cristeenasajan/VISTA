
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OPTIMIZATION_DIR = PROJECT_ROOT / "member2" / "optimization"
MATRIX_FILE = PROJECT_ROOT.parent / "VISTA_member1" / "c499_detection_matrix_recheck.json"
COMPACTION_FILE = PROJECT_ROOT / "member2" / "data" / "c499_compaction_results.json"


def test_c499_matrix_exists():
    assert MATRIX_FILE.is_file(), f"Missing matrix: {MATRIX_FILE}"


def test_c499_compaction_result_exists():
    assert COMPACTION_FILE.is_file(), f"Missing result: {COMPACTION_FILE}"


def test_c499_compaction_preserves_detectable_faults():
    matrix = json.loads(MATRIX_FILE.read_text(encoding="utf-8"))
    result = json.loads(COMPACTION_FILE.read_text(encoding="utf-8"))

    selected = {int(pattern_id) for pattern_id in result["selected_patterns"]}

    detectable = {
        fault["id"]: {int(p) for p in fault.get("detecting_patterns", [])}
        for fault in matrix["faults"]
        if fault.get("detected", False)
    }

    covered = {
        fault_id
        for fault_id, patterns in detectable.items()
        if patterns & selected
    }

    assert len(selected) == result["selected_pattern_count"] == 75
    assert len(detectable) == 750
    assert len(covered) == 750
    assert set(detectable) == covered
    assert result["coverage_preserved"] is True


def test_c499_compaction_reduction():
    result = json.loads(COMPACTION_FILE.read_text(encoding="utf-8"))

    assert result["original_patterns"] == 138
    assert result["selected_pattern_count"] == 75
    assert result["pattern_reduction_pct"] == 45.65


def test_integration_scripts_exist():
    assert (OPTIMIZATION_DIR / "member1_matrix_adapter.py").is_file()
    assert (OPTIMIZATION_DIR / "c499_pattern_compaction.py").is_file()
    assert (OPTIMIZATION_DIR / "run_c499_integration.py").is_file()

import pytest

# Import the adapter function from the project.
import sys
sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "optimization"),
)
from member1_matrix_adapter import convert_detection_matrix


def write_json(path, content):
    path.write_text(json.dumps(content), encoding="utf-8")


def test_adapter_rejects_wrong_schema(tmp_path):
    source = tmp_path / "wrong_schema.json"
    output = tmp_path / "output.json"

    write_json(source, {
        "schema_version": "9.9",
        "document": "fault_sim_report",
        "patterns": [{"index": 0}],
        "faults": [{"id": "F1", "detected": True,
                    "detecting_patterns": [0]}],
    })

    with pytest.raises(ValueError, match="schema 1.1"):
        convert_detection_matrix(source, output)


def test_adapter_rejects_wrong_document_type(tmp_path):
    source = tmp_path / "wrong_document.json"
    output = tmp_path / "output.json"

    write_json(source, {
        "schema_version": "1.1",
        "document": "wrong_report",
        "patterns": [{"index": 0}],
        "faults": [{"id": "F1", "detected": True,
                    "detecting_patterns": [0]}],
    })

    with pytest.raises(ValueError, match="fault_sim_report"):
        convert_detection_matrix(source, output)


def test_adapter_rejects_unknown_pattern_reference(tmp_path):
    source = tmp_path / "unknown_pattern.json"
    output = tmp_path / "output.json"

    write_json(source, {
        "schema_version": "1.1",
        "document": "fault_sim_report",
        "patterns": [{"index": 0}],
        "faults": [{"id": "F1", "detected": True,
                    "detecting_patterns": [999]}],
    })

    with pytest.raises(ValueError, match="unknown patterns"):
        convert_detection_matrix(source, output)

def test_c499_fresh_simulation_preserves_coverage():
    fresh_matrix_file = (
        PROJECT_ROOT.parent
        / "VISTA_member1"
        / "c499_reduced_75_matrix.json"
    )
    original_matrix_file = (
        PROJECT_ROOT.parent
        / "VISTA_member1"
        / "c499_detection_matrix_recheck.json"
    )

    assert fresh_matrix_file.is_file(), (
        f"Fresh simulation matrix missing: {fresh_matrix_file}"
    )
    assert original_matrix_file.is_file(), (
        f"Original matrix missing: {original_matrix_file}"
    )

    fresh = json.loads(
        fresh_matrix_file.read_text(encoding="utf-8")
    )
    original = json.loads(
        original_matrix_file.read_text(encoding="utf-8")
    )

    original_detectable = {
        fault["id"]
        for fault in original["faults"]
        if fault.get("detected", False)
    }
    fresh_detected = {
        fault["id"]
        for fault in fresh["faults"]
        if fault.get("detected", False)
    }

    assert len(fresh["patterns"]) == 75
    assert len(fresh["faults"]) == 758
    assert len(original_detectable) == 750
    assert original_detectable <= fresh_detected
    assert len(fresh_detected) == 750

