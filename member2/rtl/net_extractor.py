import sys
import json
import re
import os


if len(sys.argv) < 2:
    print("Usage: python net_extractor.py <verilog_file>")
    sys.exit(1)


verilog_file = sys.argv[1]


# Read Verilog
with open(verilog_file, "r") as f:
    verilog = f.read()


# Remove comments
verilog = re.sub(r"//.*", "", verilog)
verilog = re.sub(r"/\*.*?\*/", "", verilog, flags=re.S)


def clean_names(text):

    # Remove bus widths such as [7:0]
    text = re.sub(r"\[[^\]]+\]", "", text)

    names = []

    for item in text.split(","):

        item = item.strip()

        # Remove Verilog keywords
        item = re.sub(
            r"\b(input|output|wire|reg|logic|signed|unsigned)\b",
            "",
            item
        )

        # Remove brackets and newlines
        item = item.replace("(", "")
        item = item.replace(")", "")
        item = item.replace("\n", " ")

        item = item.strip()

        if item:
            names.append(item)

    return names


def extract_ports(keyword, text):

    # Find declarations such as:
    #
    # input N1, N4, N8;
    # output N223, N329;

    pattern = (
        rf"\b{keyword}\b\s+"
        rf"(.+?)"
        rf"(?=\binput\b|\boutput\b|;)"
    )

    matches = re.findall(
        pattern,
        text,
        flags=re.S
    )

    names = []

    for match in matches:
        names.extend(clean_names(match))

    # Remove duplicates
    unique_names = []

    for name in names:
        if name not in unique_names:
            unique_names.append(name)

    return unique_names


def extract_wires(text):

    pattern = r"\bwire\b\s+([^;]+);"

    matches = re.findall(
        pattern,
        text,
        flags=re.S
    )

    names = []

    for match in matches:
        names.extend(clean_names(match))

    # Remove duplicates
    unique_names = []

    for name in names:
        if name not in unique_names:
            unique_names.append(name)

    return unique_names


# Extract inputs and outputs
inputs = extract_ports(
    "input",
    verilog
)

outputs = extract_ports(
    "output",
    verilog
)


# Extract internal wires
internal_nets = extract_wires(
    verilog
)


# Remove ports from internal nets
internal_nets = [
    net
    for net in internal_nets
    if net not in inputs
    and net not in outputs
]


# Find gates
gate_pattern = (
    r"\b"
    r"(and|or|nand|nor|xor|xnor|not|buf)"
    r"\s+\w+\s*\("
)

gate_matches = re.findall(
    gate_pattern,
    verilog
)


# All nets
all_nets = (
    inputs
    + internal_nets
    + outputs
)


# Create result
result = {
    "verilog_file": os.path.basename(verilog_file),
    "inputs": inputs,
    "outputs": outputs,
    "internal_nets": internal_nets,
    "all_nets": all_nets,
    "gate_count": len(gate_matches)
}


# Display
print()
print("RTL Analysis")
print("============")
print("File:", verilog_file)
print("Inputs:", inputs)
print("Outputs:", outputs)
print("Internal nets:", internal_nets)
print("All nets:", all_nets)
print("Gate count:", len(gate_matches))


# Save
base_name = os.path.splitext(
    os.path.basename(verilog_file)
)[0]

output_file = os.path.join(
    "data",
    f"{base_name}_rtl_analysis.json"
)


with open(output_file, "w") as f:
    json.dump(
        result,
        f,
        indent=4
    )


print()
print("Analysis saved to:")
print(output_file)