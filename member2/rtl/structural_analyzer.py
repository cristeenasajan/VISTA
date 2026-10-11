import sys
import json
import re
import os
from collections import defaultdict, deque


# ============================================================
# 1. CHECK ARGUMENT
# ============================================================

if len(sys.argv) < 2:
    print("Usage: python structural_analyzer.py <verilog_file>")
    sys.exit(1)


VERILOG_FILE = sys.argv[1]


# ============================================================
# 2. READ VERILOG
# ============================================================

with open(VERILOG_FILE, "r") as file:
    verilog = file.read()


# Remove comments
verilog = re.sub(
    r"//.*",
    "",
    verilog
)

verilog = re.sub(
    r"/\*.*?\*/",
    "",
    verilog,
    flags=re.S
)


# ============================================================
# 3. EXTRACT INPUTS / OUTPUTS
# ============================================================

def extract_ports(keyword):

    pattern = (
        rf"\b{keyword}\b\s+"
        rf"([^;]+);"
    )

    matches = re.findall(
        pattern,
        verilog,
        flags=re.S
    )

    names = []

    for match in matches:

        # Remove declarations that accidentally span
        # into another section
        match = re.sub(
            r"\b(input|output|wire|reg|logic)\b",
            "",
            match
        )

        match = re.sub(
            r"\[[^\]]+\]",
            "",
            match
        )

        for item in match.split(","):

            name = item.strip()

            name = name.replace(
                "\n",
                " "
            ).strip()

            if (
                name
                and
                re.fullmatch(
                    r"[A-Za-z_][A-Za-z0-9_]*",
                    name
                )
                and
                name not in names
            ):

                names.append(name)

    return names


inputs = extract_ports("input")

outputs = extract_ports("output")


# ============================================================
# 4. EXTRACT GATES
# ============================================================

gate_pattern = re.compile(
    r"\b"
    r"(and|or|nand|nor|xor|xnor|not|buf)"
    r"\s+"
    r"([A-Za-z_][A-Za-z0-9_]*)"
    r"\s*"
    r"\("
    r"([^;]+)"
    r"\);",
    flags=re.IGNORECASE
)


gates = []


for match in gate_pattern.finditer(verilog):

    gate_type = match.group(1).lower()

    gate_name = match.group(2)

    connection_text = match.group(3)


    nets = []

    for item in connection_text.split(","):

        net = item.strip()

        if net:
            nets.append(net)


    if len(nets) < 2:
        continue


    output_net = nets[0]

    input_nets = nets[1:]


    gates.append({
        "gate_name": gate_name,
        "gate_type": gate_type,
        "output": output_net,
        "inputs": input_nets
    })


# ============================================================
# 5. BUILD GRAPH INFORMATION
# ============================================================

driver = {}

fanout = defaultdict(int)

gate_for_net = {}

fanin = {}


for gate in gates:

    output_net = gate["output"]

    input_nets = gate["inputs"]


    driver[output_net] = gate

    gate_for_net[output_net] = (
        gate["gate_type"]
    )

    fanin[output_net] = len(
        input_nets
    )


    for net in input_nets:

        fanout[net] += 1


# Make sure every known net exists
all_nets = set(
    inputs +
    outputs +
    list(driver.keys())
)


for net in all_nets:

    fanout.setdefault(
        net,
        0
    )


# ============================================================
# 6. CALCULATE LOGIC DEPTH
# ============================================================

logic_depth = {}


for net in inputs:

    logic_depth[net] = 0


changed = True


while changed:

    changed = False


    for gate in gates:

        output_net = gate["output"]

        input_nets = gate["inputs"]


        if all(
            net in logic_depth
            for net in input_nets
        ):

            new_depth = (
                max(
                    logic_depth[net]
                    for net in input_nets
                )
                + 1
            )


            if (
                output_net not in logic_depth
                or
                new_depth >
                logic_depth[output_net]
            ):

                logic_depth[output_net] = (
                    new_depth
                )

                changed = True


# Unresolved nets get depth -1
for net in all_nets:

    logic_depth.setdefault(
        net,
        -1
    )


# ============================================================
# 7. CALCULATE DISTANCE TO OUTPUT
# ============================================================

# Build forward graph:
#
# input net → gate output

forward_graph = defaultdict(list)


for gate in gates:

    output_net = gate["output"]

    for input_net in gate["inputs"]:

        forward_graph[input_net].append(
            output_net
        )


# Reverse BFS starting from primary outputs

distance_to_output = {}

queue = deque()


for output_net in outputs:

    distance_to_output[output_net] = 0

    queue.append(output_net)


# Reverse connections
reverse_graph = defaultdict(list)


for source, destinations in forward_graph.items():

    for destination in destinations:

        reverse_graph[destination].append(
            source
        )


while queue:

    current = queue.popleft()

    current_distance = (
        distance_to_output[current]
    )


    for previous in reverse_graph[current]:

        new_distance = (
            current_distance + 1
        )


        if (
            previous not in distance_to_output
            or
            new_distance <
            distance_to_output[previous]
        ):

            distance_to_output[previous] = (
                new_distance
            )

            queue.append(previous)


for net in all_nets:

    distance_to_output.setdefault(
        net,
        -1
    )


# ============================================================
# 8. BUILD STRUCTURAL FEATURES
# ============================================================

features = []


for net in sorted(all_nets):

    if net in inputs:

        net_type = "primary_input"

    elif net in outputs:

        net_type = "primary_output"

    else:

        net_type = "internal"


    gate_type = gate_for_net.get(
        net,
        "INPUT"
    )


    features.append({

        "net":
            net,

        "net_type":
            net_type,

        "gate_type":
            gate_type,

        "fanin":
            fanin.get(net, 0),

        "fanout":
            fanout.get(net, 0),

        "logic_depth":
            logic_depth.get(net, -1),

        "distance_to_output":
            distance_to_output.get(net, -1)
    })


# ============================================================
# 9. SAVE
# ============================================================

base_name = os.path.splitext(
    os.path.basename(VERILOG_FILE)
)[0]


# ============================================================
# SAVE STRUCTURAL FEATURES
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "member2",
    "data"
)

os.makedirs(
    DATA_DIR,
    exist_ok=True
)

output_file = os.path.join(
    DATA_DIR,
    f"{base_name}_structural_features.json"
)

result = {

    "benchmark":
        base_name,

    "gate_count":
        len(gates),

    "features":
        features
}


with open(
    output_file,
    "w"
) as file:

    json.dump(
        result,
        file,
        indent=4
    )


# ============================================================
# 10. DISPLAY
# ============================================================

print()
print("VISTA Structural Analysis")
print("=========================")
print()

print(
    "Benchmark:",
    base_name
)

print(
    "Gates:",
    len(gates)
)

print(
    "Nets analyzed:",
    len(features)
)

print()


# Show important suspect nets
suspect_nets = [
    "N259",
    "N347",
    "N379"
]


print("Suspect fault locations:")
print("------------------------")


for net in suspect_nets:

    for item in features:

        if item["net"] == net:

            print(item)


print()
print("Structural features saved to:")
print(output_file)