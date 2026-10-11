import sys
import json
import os


# ============================================================
# 1. CHECK INPUT
# ============================================================

if len(sys.argv) < 2:
    print("Usage: python fault_generator.py <rtl_analysis.json>")
    sys.exit(1)


analysis_file = sys.argv[1]


# ============================================================
# 2. READ RTL ANALYSIS
# ============================================================

with open(analysis_file, "r") as file:
    analysis = json.load(file)


# ============================================================
# 3. GET NETS
# ============================================================

all_nets = analysis["all_nets"]


# ============================================================
# 4. GENERATE STUCK-AT FAULTS
# ============================================================

faults = []

fault_number = 1

for net in all_nets:

    # Stuck-at-0
    faults.append({
        "fault_id": f"F{fault_number:03d}",
        "net": net,
        "fault_type": "SA0"
    })

    fault_number += 1

    # Stuck-at-1
    faults.append({
        "fault_id": f"F{fault_number:03d}",
        "net": net,
        "fault_type": "SA1"
    })

    fault_number += 1


# ============================================================
# 5. DISPLAY
# ============================================================

print()
print("Automatic Fault Generation")
print("===========================")

for fault in faults:

    print(
        fault["fault_id"],
        "->",
        fault["net"],
        fault["fault_type"]
    )


print()
print("Total faults:", len(faults))


# ============================================================
# 6. CREATE OUTPUT FILENAME
# ============================================================

benchmark_name = os.path.splitext(
    os.path.basename(
        analysis_file
    )
)[0]

# Remove "_rtl_analysis"
benchmark_name = benchmark_name.replace(
    "_rtl_analysis",
    ""
)


output_file = os.path.join(
    "data",
    f"{benchmark_name}_faults.json"
)


# ============================================================
# 7. SAVE FAULT LIST
# ============================================================

with open(
    output_file,
    "w"
) as file:

    json.dump(
        faults,
        file,
        indent=4
    )


print()
print("Fault list saved to:")
print(output_file)