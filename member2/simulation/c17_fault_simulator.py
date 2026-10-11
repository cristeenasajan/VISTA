import json
import subprocess
from pathlib import Path
import os
import sys
import random


# ============================================================
# 1. CHECK ARGUMENTS
# ============================================================

if len(sys.argv) < 3:
    print("Usage:")
    print("python fault_simulator.py <faults.json> <rtl_analysis.json>")
    sys.exit(1)


FAULT_FILE = Path(sys.argv[1])
RTL_FILE = Path(sys.argv[2])


# ============================================================
# 2. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

BENCHMARK_DIR = BASE_DIR / "benchmarks"

DATA_DIR = BASE_DIR / "member2" / "data"


# ============================================================
# 3. READ RTL ANALYSIS
# ============================================================

with open(RTL_FILE, "r") as file:
    rtl = json.load(file)


benchmark_name = Path(
    rtl["verilog_file"]
).stem


RTL_PATH = BENCHMARK_DIR / rtl["verilog_file"]


PRIMARY_INPUTS = rtl["inputs"]
OUTPUTS = rtl["outputs"]


# ============================================================
# 4. FAULT DIRECTORY
# ============================================================

FAULT_DIR = (
    BENCHMARK_DIR /
    f"{benchmark_name}_generated_faults"
)


# ============================================================
# 5. OUTPUT FILE
# ============================================================

OUTPUT_FILE = (
    DATA_DIR /
    f"{benchmark_name}_simulation_results.json"
)


# ============================================================
# 6. ICARUS
# ============================================================

# Set MSYS2_UCRT64_BIN if Icarus Verilog is installed somewhere
# other than the default MSYS2 UCRT64 directory.
MSYS2_BIN = os.environ.get(
    "MSYS2_UCRT64_BIN",
    r"C:\msys64\ucrt64\bin"
)

ENV = os.environ.copy()
ENV["PATH"] = MSYS2_BIN + os.pathsep + ENV.get("PATH", "")

# Resolve executables from the configured PATH, with an explicit
# fallback to the configured MSYS2 directory.
import shutil

IVERILOG = Path(
    shutil.which("iverilog.exe", path=ENV["PATH"])
    or (Path(MSYS2_BIN) / "iverilog.exe")
)

VVP = Path(
    shutil.which("vvp.exe", path=ENV["PATH"])
    or (Path(MSYS2_BIN) / "vvp.exe")
)

if not IVERILOG.is_file():
    raise FileNotFoundError(
        f"Icarus Verilog compiler not found: {IVERILOG}. "
        "Set MSYS2_UCRT64_BIN to your MSYS2 UCRT64 bin directory."
    )

if not VVP.is_file():
    raise FileNotFoundError(
        f"Icarus Verilog runtime not found: {VVP}. "
        "Set MSYS2_UCRT64_BIN to your MSYS2 UCRT64 bin directory."
    )


# ============================================================
# 7. GENERATE SAME PATTERNS AS FAULT INJECTOR
# ============================================================

num_inputs = len(PRIMARY_INPUTS)

if num_inputs <= 10:

    num_patterns = 2 ** num_inputs

    exhaustive = True

else:

    num_patterns = 1024

    exhaustive = False


patterns = []

if exhaustive:

    for i in range(num_patterns):
        patterns.append(i)

else:

    random.seed(42)

    max_value = 2 ** num_inputs

    # all zero
    patterns.append(0)

    # all one
    patterns.append(max_value - 1)

    while len(patterns) < num_patterns:

        value = random.randrange(
            0,
            max_value
        )

        if value not in patterns:
            patterns.append(value)


# ============================================================
# 8. CREATE GOLDEN TESTBENCH
# ============================================================

golden_tb = (
    BENCHMARK_DIR /
    f"{benchmark_name}_golden_tb.v"
)

golden_sim = (
    BENCHMARK_DIR /
    f"{benchmark_name}_golden_sim"
)


input_declarations = "\n".join(
    f"    reg {signal};"
    for signal in PRIMARY_INPUTS
)


output_declarations = "\n".join(
    f"    wire {signal};"
    for signal in OUTPUTS
)


connections = []

for signal in PRIMARY_INPUTS:

    connections.append(
        f"        .{signal}({signal})"
    )

for signal in OUTPUTS:

    connections.append(
        f"        .{signal}({signal})"
    )


port_text = ",\n".join(
    connections
)


input_list = ", ".join(
    PRIMARY_INPUTS
)


output_list = ", ".join(
    OUTPUTS
)


input_width = len(PRIMARY_INPUTS)
output_width = len(OUTPUTS)


pattern_lines = []

for pattern in patterns:

    binary_pattern = format(
        pattern,
        f"0{input_width}b"
    )

    pattern_lines.append(
        f"        {{{input_list}}} = "
        f"{input_width}'b{binary_pattern};"
    )

    pattern_lines.append(
        "        #1;"
    )

    pattern_lines.append(
        f'        $display('
        f'"INPUT=%0{input_width}b '
        f'OUTPUT=%0{output_width}b", '
        f'{input_width}\'b{binary_pattern}, '
        f'{{{output_list}}}'
        f');'
    )

    pattern_lines.append("")


pattern_text = "\n".join(
    pattern_lines
)


golden_testbench = f"""`timescale 1ns/1ps

module golden_tb;

{input_declarations}

{output_declarations}

    {benchmark_name} dut (
{port_text}
    );

    initial begin

{pattern_text}

        $finish;

    end

endmodule
"""


with open(
    golden_tb,
    "w"
) as file:

    file.write(
        golden_testbench
    )


# ============================================================
# 9. COMPILE GOLDEN
# ============================================================

print()
print("VISTA Fault Simulation")
print("======================")
print("Benchmark:", benchmark_name)
print("Inputs:", len(PRIMARY_INPUTS))
print("Outputs:", len(OUTPUTS))
print("Faults file:", FAULT_FILE)
print("Patterns:", len(patterns))

if exhaustive:
    print("Pattern mode: Exhaustive")
else:
    print("Pattern mode: Deterministic random")

print()
print("Generating golden simulation...")


compile_result = subprocess.run(
    [
        str(IVERILOG),
        "-o",
        str(golden_sim),
        str(RTL_PATH),
        str(golden_tb)
    ],
    capture_output=True,
    text=True,
    env=ENV
)


if compile_result.returncode != 0:

    print()
    print("ERROR: Golden compilation failed")
    print(compile_result.stderr)

    sys.exit(1)


# ============================================================
# 10. RUN GOLDEN
# ============================================================

run_result = subprocess.run(
    [
        str(VVP),
        str(golden_sim)
    ],
    capture_output=True,
    text=True,
    env=ENV
)


if run_result.returncode != 0:

    print()
    print("ERROR: Golden simulation failed")
    print(run_result.stderr)

    sys.exit(1)


# ============================================================
# 11. PARSE GOLDEN OUTPUT
# ============================================================

golden = {}

for line in run_result.stdout.splitlines():

    line = line.strip()

    if not line.startswith("INPUT="):
        continue

    parts = line.split()

    pattern = parts[0].split("=")[1]

    output = parts[1].split("=")[1]

    golden[pattern] = output


print(
    "Golden patterns generated:",
    len(golden)
)


# ============================================================
# 12. READ FAULT LIST
# ============================================================

with open(
    FAULT_FILE,
    "r"
) as file:

    faults = json.load(file)


print(
    "Total faults:",
    len(faults)
)

print()


# ============================================================
# 13. SIMULATE EVERY FAULT
# ============================================================

results = []


for index, fault in enumerate(
    faults,
    start=1
):

    fault_id = fault["fault_id"]

    fault_type = fault["fault_type"]

    net = fault["net"]


    testbench = (
        FAULT_DIR /
        f"{benchmark_name}_"
        f"{fault_id}_"
        f"{fault_type}_tb.v"
    )


    executable = (
        FAULT_DIR /
        f"{benchmark_name}_"
        f"{fault_id}_"
        f"{fault_type}_sim"
    )


    print(
        f"[{index}/{len(faults)}] "
        f"{fault_id} -> "
        f"{net} {fault_type}"
    )


    # --------------------------------------------------------
    # Compile
    # --------------------------------------------------------

    compile_result = subprocess.run(
        [
            str(IVERILOG),
            "-o",
            str(executable),
            str(RTL_PATH),
            str(testbench)
        ],
        capture_output=True,
        text=True,
        env=ENV
    )


    if compile_result.returncode != 0:

        print(
            "  ERROR: Compilation failed"
        )

        results.append({

            "fault_id":
                fault_id,

            "net":
                net,

            "fault_type":
                fault_type,

            "error":
                "Compilation failed",

            "details":
                compile_result.stderr
        })

        continue


    # --------------------------------------------------------
    # Run
    # --------------------------------------------------------

    run_result = subprocess.run(
        [
            str(VVP),
            str(executable)
        ],
        capture_output=True,
        text=True,
        env=ENV
    )


    if run_result.returncode != 0:

        print(
            "  ERROR: Simulation failed"
        )

        results.append({

            "fault_id":
                fault_id,

            "net":
                net,

            "fault_type":
                fault_type,

            "error":
                "Simulation failed",

            "details":
                run_result.stderr
        })

        continue


    # --------------------------------------------------------
    # Compare outputs
    # --------------------------------------------------------

    detected_patterns = []


    for line in run_result.stdout.splitlines():

        line = line.strip()

        if not line.startswith("FAULT="):
            continue


        parts = line.split()

        pattern = (
            parts[1]
            .split("=")[1]
        )


        faulty_output = (
            parts[2]
            .split("=")[1]
        )


        golden_output = golden.get(
            pattern
        )


        if (
            golden_output is not None
            and
            faulty_output != golden_output
        ):

            detected_patterns.append(
                pattern
            )


    detection_count = len(
        detected_patterns
    )


    # --------------------------------------------------------
    # Difficulty
    # --------------------------------------------------------

    if detection_count == 0:

        difficulty = "Hard"

    elif detection_count <= 8:

        difficulty = "Medium"

    else:

        difficulty = "Easy"


    print(
        f"    Detected by "
        f"{detection_count} patterns"
    )


    results.append({

        "fault_id":
            fault_id,

        "net":
            net,

        "fault_type":
            fault_type,

        "detected_patterns":
            detected_patterns,

        "detection_count":
            detection_count,

        "difficulty":
            difficulty
    })


    # Remove temporary executable

    try:

        executable.unlink()

    except FileNotFoundError:

        pass


# ============================================================
# 14. SAVE RESULTS
# ============================================================

with open(
    OUTPUT_FILE,
    "w"
) as file:

    json.dump(
        results,
        file,
        indent=4
    )


# ============================================================
# 15. CLEAN GOLDEN FILES
# ============================================================

try:
    golden_sim.unlink()
except FileNotFoundError:
    pass

try:
    golden_tb.unlink()
except FileNotFoundError:
    pass


# ============================================================
# 16. SUMMARY
# ============================================================

successful = sum(
    1
    for result in results
    if "error" not in result
)


failed = len(results) - successful


detected_faults = sum(
    1
    for result in results
    if (
        "error" not in result
        and
        result["detection_count"] > 0
    )
)


print()
print("======================")
print("Simulation complete")
print("======================")
print()
print("Faults processed:", len(results))
print("Successful:", successful)
print("Failed:", failed)
print("Detected faults:", detected_faults)
print(
    "Fault coverage:",
    f"{(detected_faults / len(faults)) * 100:.2f}%"
)
print()
print("Results saved to:")
print(OUTPUT_FILE)