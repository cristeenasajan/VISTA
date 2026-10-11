import json
import os
import sys
import random


# ============================================================
# 1. CHECK ARGUMENTS
# ============================================================

if len(sys.argv) < 3:
    print("Usage:")
    print("python fault_injector.py <faults.json> <rtl_analysis.json>")
    sys.exit(1)


FAULT_FILE = sys.argv[1]
RTL_FILE = sys.argv[2]


# ============================================================
# 2. READ FILES
# ============================================================

with open(FAULT_FILE, "r") as file:
    faults = json.load(file)

with open(RTL_FILE, "r") as file:
    rtl = json.load(file)


# ============================================================
# 3. DETERMINE BENCHMARK NAME
# ============================================================

benchmark_name = os.path.splitext(
    os.path.basename(
        rtl["verilog_file"]
    )
)[0]


# ============================================================
# 4. GET INPUTS / OUTPUTS
# ============================================================

primary_inputs = rtl["inputs"]
outputs = rtl["outputs"]


# ============================================================
# 5. OUTPUT DIRECTORY
# ============================================================

# Find the VISTA project root automatically.
#
# Current file:
# VISTA\member2\rtl\fault_injector.py
#
# Going:
# rtl -> member2 -> VISTA
#
# gives us the project root.

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)


OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "benchmarks",
    f"{benchmark_name}_generated_faults"
)


# Create the directory if it does not exist.
os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# 6. DETERMINE NUMBER OF PATTERNS
# ============================================================

num_inputs = len(primary_inputs)

if num_inputs <= 10:

    # Small circuits can be exhaustively tested.
    num_patterns = 2 ** num_inputs

    exhaustive = True

else:

    # Large circuits cannot be exhaustively tested.
    num_patterns = 1024

    exhaustive = False


# ============================================================
# 7. GENERATE PATTERNS
# ============================================================

patterns = []


if exhaustive:

    for i in range(num_patterns):
        patterns.append(i)

else:

    # Deterministic random patterns.
    # Using a fixed seed makes the experiment reproducible.
    random.seed(42)

    max_value = 2 ** num_inputs

    # Include all-zero pattern.
    patterns.append(0)

    # Include all-one pattern.
    patterns.append(max_value - 1)

    # Generate remaining patterns.
    while len(patterns) < num_patterns:

        value = random.randrange(
            0,
            max_value
        )

        if value not in patterns:
            patterns.append(value)


# ============================================================
# 8. DISPLAY INFORMATION
# ============================================================

print()
print("Automatic Fault Injection")
print("==========================")

print(
    "Benchmark:",
    benchmark_name
)

print(
    "Primary inputs:",
    len(primary_inputs)
)

print(
    "Outputs:",
    len(outputs)
)

print(
    "Faults:",
    len(faults)
)

print(
    "Patterns:",
    len(patterns)
)

if exhaustive:

    print(
        "Pattern mode: Exhaustive"
    )

else:

    print(
        "Pattern mode: Deterministic random"
    )


# ============================================================
# 9. GENERATE TESTBENCHES
# ============================================================

for fault in faults:

    fault_id = fault["fault_id"]

    net = fault["net"]

    fault_type = fault["fault_type"]


    # --------------------------------------------------------
    # Stuck-at value
    # --------------------------------------------------------

    if fault_type == "SA0":

        stuck_value = "1'b0"

    else:

        stuck_value = "1'b1"


    # --------------------------------------------------------
    # Primary input vs internal/output net
    # --------------------------------------------------------

    if net in primary_inputs:

        force_statement = (
            f"force {net} = {stuck_value};"
        )

        release_statement = (
            f"release {net};"
        )

    else:

        force_statement = (
            f"force dut.{net} = {stuck_value};"
        )

        release_statement = (
            f"release dut.{net};"
        )


    # --------------------------------------------------------
    # Generate input declarations
    # --------------------------------------------------------

    input_declarations = "\n".join(
        f"    reg {signal};"
        for signal in primary_inputs
    )


    # --------------------------------------------------------
    # Generate output declarations
    # --------------------------------------------------------

    output_declarations = "\n".join(
        f"    wire {signal};"
        for signal in outputs
    )


    # --------------------------------------------------------
    # Generate DUT port connections
    # --------------------------------------------------------

    port_connections = []

    for signal in primary_inputs:

        port_connections.append(
            f"        .{signal}({signal})"
        )


    for signal in outputs:

        port_connections.append(
            f"        .{signal}({signal})"
        )


    port_text = ",\n".join(
        port_connections
    )


    # --------------------------------------------------------
    # Input/output lists
    # --------------------------------------------------------

    input_list = ", ".join(
        primary_inputs
    )

    output_list = ", ".join(
        outputs
    )


    input_width = len(
        primary_inputs
    )

    output_width = len(
        outputs
    )


    # --------------------------------------------------------
    # Build pattern statements
    # --------------------------------------------------------

    pattern_lines = []


    for pattern_number, pattern in enumerate(patterns):

        binary_pattern = format(
            pattern,
            f"0{input_width}b"
        )


        # Apply input pattern.
        pattern_lines.append(
            f"            "
            f"{{{input_list}}} = "
            f"{input_width}'b{binary_pattern};"
        )


        # Allow the circuit to settle.
        pattern_lines.append(
            "            #1;"
        )


        # Apply stuck-at fault.
        pattern_lines.append(
            f"            {force_statement}"
        )


        # Allow fault effect to propagate.
        pattern_lines.append(
            "            #9;"
        )


        # Print faulty output.
        pattern_lines.append(
            f'            $display('
            f'"FAULT={fault_id} '
            f'PATTERN=%0{input_width}b '
            f'OUTPUT=%0{output_width}b", '
            f'{input_width}\'b{binary_pattern}, '
            f'{{{output_list}}}'
            f');'
        )


        # Release fault before next pattern.
        pattern_lines.append(
            f"            {release_statement}"
        )


        pattern_lines.append("")


    pattern_text = "\n".join(
        pattern_lines
    )


    # ========================================================
    # 10. CREATE TESTBENCH
    # ========================================================

    testbench = f"""`timescale 1ns/1ps

module fault_tb;

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


    # ========================================================
    # 11. SAVE TESTBENCH
    # ========================================================

    filename = (
        f"{benchmark_name}_"
        f"{fault_id}_"
        f"{fault_type}_tb.v"
    )


    filepath = os.path.join(
        OUTPUT_DIR,
        filename
    )


    with open(
        filepath,
        "w"
    ) as file:

        file.write(
            testbench
        )


# ============================================================
# 12. FINAL MESSAGE
# ============================================================

print()

print(
    "Generated",
    len(faults),
    "fault testbenches."
)

print(
    "Patterns per fault:",
    len(patterns)
)

print(
    "Output directory:"
)

print(
    OUTPUT_DIR
)