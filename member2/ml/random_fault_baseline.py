import json
import random
from pathlib import Path


# ============================================================
# VISTA RANDOM FAULT PRIORITIZATION BASELINE
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "member2" / "data"

OUTPUT_FILE = (
    DATA_DIR
    / "random_fault_baseline_results.json"
)


# ============================================================
# LOAD SIMULATION RESULTS
# ============================================================

benchmarks = [
    "c17",
    "c432",
    "c499"
]


all_results = []


for benchmark in benchmarks:

    print()
    print("========================================")
    print("BENCHMARK:", benchmark.upper())
    print("========================================")


    simulation_file = (
        DATA_DIR
        / f"{benchmark}_simulation_results.json"
    )


    with open(
        simulation_file,
        "r"
    ) as file:

        simulation = json.load(file)


    total_faults = len(simulation)


    # --------------------------------------------------------
    # Identify genuinely hard faults using VISTA's
    # original diagnosis definition.
    #
    # 0 detections     -> Hard
    # 1-8 detections   -> Medium
    # >8 detections    -> Easy
    # --------------------------------------------------------

    hard_faults = []


    for fault in simulation:

        detection_count = int(
            fault.get(
                "detection_count",
                0
            )
        )


        if detection_count == 0:

            hard_faults.append(
                fault["fault_id"]
            )


    hard_set = set(
        hard_faults
    )


    print(
        "Total faults:",
        total_faults
    )


    print(
        "Hard faults:",
        len(hard_faults)
    )


    # ========================================================
    # REPEAT RANDOM EXPERIMENT
    # ========================================================

    repetitions = 1000

    percentages = [
        10,
        20,
        30
    ]


    accumulated_recall = {

        10: 0.0,
        20: 0.0,
        30: 0.0

    }


    random.seed(42)


    for _ in range(
        repetitions
    ):

        fault_ids = [

            fault["fault_id"]

            for fault in simulation

        ]


        random.shuffle(
            fault_ids
        )


        for percentage in percentages:

            k = max(

                1,

                int(
                    total_faults
                    *
                    percentage
                    /
                    100
                )

            )


            selected = set(
                fault_ids[:k]
            )


            hard_found = len(
                selected
                &
                hard_set
            )


            if len(hard_set) > 0:

                recall = (

                    hard_found
                    /
                    len(hard_set)

                )

            else:

                recall = 0.0


            accumulated_recall[
                percentage
            ] += recall


    # ========================================================
    # AVERAGE RANDOM RECALL
    # ========================================================

    average_recall = {}


    for percentage in percentages:

        value = (

            accumulated_recall[
                percentage
            ]
            /
            repetitions

        )


        average_recall[
            percentage
        ] = value


        print()

        print(
            f"Random top {percentage}% "
            f"Hard-fault recall:",
            f"{value * 100:.2f}%"
        )


    # ========================================================
    # SAVE BENCHMARK RESULT
    # ========================================================

    all_results.append({

        "benchmark":
            benchmark,

        "total_faults":
            total_faults,

        "hard_faults":
            len(hard_faults),

        "repetitions":
            repetitions,

        "average_hard_fault_recall":
            average_recall

    })


# ============================================================
# SAVE COMPLETE RESULT
# ============================================================

final_result = {

    "experiment":
        "Random fault prioritization baseline",

    "repetitions":
        1000,

    "results":
        all_results

}


with open(
    OUTPUT_FILE,
    "w"
) as file:

    json.dump(
        final_result,
        file,
        indent=4
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print(
    "========================================"
)

print(
    "RANDOM BASELINE COMPLETE"
)

print(
    "========================================"
)


for result in all_results:

    print()

    print(
        "Held-out:",
        result["benchmark"].upper()
    )


    recall = result[
        "average_hard_fault_recall"
    ]


    for percentage in [
        10,
        20,
        30
    ]:

        print(

            f"Top {percentage}% -> "
            f"{recall[percentage] * 100:.2f}% "
            f"Hard-fault recall"

        )


print()

print(
    "Results saved to:"
)

print(
    OUTPUT_FILE
)