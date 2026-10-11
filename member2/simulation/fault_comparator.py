import re
import json


def read_simulation_file(filename):

    results = {}

    with open(filename, "r") as file:

        for line in file:

            match = re.search(
                r"A=(\d) B=(\d) Y=(\d)",
                line
            )

            if match:

                A = match.group(1)
                B = match.group(2)
                Y = match.group(3)

                pattern = A + B

                results[pattern] = Y

    return results


def compare_fault(golden, faulty, fault_id):

    results = []

    for pattern in golden:

        golden_output = golden[pattern]
        faulty_output = faulty[pattern]

        detected = golden_output != faulty_output

        results.append({
            "pattern_id": pattern,
            "fault_id": fault_id,
            "detected": detected
        })

    return results


golden = read_simulation_file(
    "../../benchmarks/golden_output.txt"
)

sa0 = read_simulation_file(
    "../../benchmarks/faulty_output.txt"
)

sa1 = read_simulation_file(
    "../../benchmarks/faulty_sa1_output.txt"
)


all_results = []

all_results.extend(
    compare_fault(
        golden,
        sa0,
        "Y_SA0"
    )
)

all_results.extend(
    compare_fault(
        golden,
        sa1,
        "Y_SA1"
    )
)


for result in all_results:

    print(
        "Pattern:", result["pattern_id"],
        "| Fault:", result["fault_id"],
        "| Detected:", result["detected"]
    )


with open(
    "../data/real_simulation_results.json",
    "w"
) as file:

    json.dump(
        all_results,
        file,
        indent=4
    )


print()
print("Results saved to:")
print("../data/real_simulation_results.json")