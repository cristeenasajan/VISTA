import json
import random
from pathlib import Path


# ============================================================
# VISTA RELATIVE RANDOM FAULT PRIORITIZATION BASELINE
# ============================================================
#
# Purpose:
#
# Compare ML-guided fault prioritization against RANDOM
# fault ordering using exactly the same target definition.
#
# Relative difficulty is calculated separately for each
# benchmark:
#
#   Bottom 25% detection count -> Hard
#   Middle 50%                -> Medium
#   Top 25%                   -> Easy
#
# This is the SAME label definition used by:
#
#   relative_multi_benchmark_ml_dataset.json
#
# Therefore the comparison is:
#
#       RANDOM vs ML
#
# on the SAME faults and SAME target.
# ============================================================


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = (
    BASE_DIR
    / "member2"
    / "data"
)


OUTPUT_FILE = (
    DATA_DIR
    / "random_relative_baseline_results.json"
)


# ============================================================
# 2. BENCHMARKS
# ============================================================

BENCHMARKS = [

    "c17",

    "c432",

    "c499"

]


# ============================================================
# 3. SETTINGS
# ============================================================

REPETITIONS = 1000

PERCENTAGES = [

    10,

    20,

    30

]


# ============================================================
# 4. CREATE RELATIVE LABELS
# ============================================================

def create_relative_labels(
    simulation_results
):

    detection_counts = [

        int(
            fault.get(
                "detection_count",
                0
            )
        )

        for fault in simulation_results

    ]


    if not detection_counts:

        return []


    sorted_counts = sorted(
        detection_counts
    )


    total = len(
        sorted_counts
    )


    # --------------------------------------------------------
    # Bottom 25%
    # --------------------------------------------------------

    hard_index = max(

        0,

        int(
            total * 0.25
        ) - 1

    )


    # --------------------------------------------------------
    # Top 25%
    # --------------------------------------------------------

    easy_index = min(

        total - 1,

        int(
            total * 0.75
        )

    )


    hard_threshold = (

        sorted_counts[
            hard_index
        ]

    )


    easy_threshold = (

        sorted_counts[
            easy_index
        ]

    )


    labels = []


    for count in detection_counts:

        if count <= hard_threshold:

            labels.append(
                "Hard"
            )

        elif count >= easy_threshold:

            labels.append(
                "Easy"
            )

        else:

            labels.append(
                "Medium"
            )


    return labels


# ============================================================
# 5. MAIN EXPERIMENT
# ============================================================

print()

print(
    "VISTA Relative Random Fault Baseline"
)

print(
    "====================================="
)

print()

print(
    "Target:",
    "relative difficulty"
)

print(
    "Hard = bottom 25% detection counts"
)

print(
    "Repetitions:",
    REPETITIONS
)


all_results = []


# ============================================================
# 6. PROCESS EACH BENCHMARK
# ============================================================

for benchmark in BENCHMARKS:

    print()

    print(
        "========================================"
    )

    print(
        "BENCHMARK:",
        benchmark.upper()
    )

    print(
        "========================================"
    )


    # --------------------------------------------------------
    # Load simulation results
    # --------------------------------------------------------

    simulation_file = (

        DATA_DIR
        /
        f"{benchmark}_simulation_results.json"

    )


    if not simulation_file.exists():

        raise FileNotFoundError(

            f"Simulation file not found:\n"
            f"{simulation_file}"

        )


    with open(
        simulation_file,
        "r"
    ) as file:

        simulation_results = json.load(
            file
        )


    # --------------------------------------------------------
    # Create EXACTLY the same relative labels used by ML
    # --------------------------------------------------------

    labels = create_relative_labels(
        simulation_results
    )


    # --------------------------------------------------------
    # Build fault records
    # --------------------------------------------------------

    faults = []


    for index, fault in enumerate(
        simulation_results
    ):

        faults.append({

            "fault_id":
                fault["fault_id"],

            "net":
                fault.get(
                    "net",
                    ""
                ),

            "fault_type":
                fault.get(
                    "fault_type",
                    ""
                ),

            "detection_count":
                int(
                    fault.get(
                        "detection_count",
                        0
                    )
                ),

            "relative_difficulty":
                labels[index]

        })


    # --------------------------------------------------------
    # Identify relative Hard faults
    # --------------------------------------------------------

    hard_faults = [

        fault["fault_id"]

        for fault in faults

        if fault[
            "relative_difficulty"
        ]
        ==
        "Hard"

    ]


    hard_set = set(
        hard_faults
    )


    total_faults = len(
        faults
    )


    hard_count = len(
        hard_faults
    )


    print()

    print(
        "Total faults:",
        total_faults
    )


    print(
        "Relative Hard faults:",
        hard_count
    )


    # ========================================================
    # 7. RANDOM EXPERIMENT
    # ========================================================

    accumulated_recall = {

        10: 0.0,

        20: 0.0,

        30: 0.0

    }


    # Use deterministic seed so experiment is reproducible.

    random_generator = random.Random(
        42
    )


    for repetition in range(
        REPETITIONS
    ):

        # ----------------------------------------------------
        # Create random ordering
        # ----------------------------------------------------

        shuffled_faults = [

            fault["fault_id"]

            for fault in faults

        ]


        random_generator.shuffle(
            shuffled_faults
        )


        # ----------------------------------------------------
        # Evaluate top 10/20/30%
        # ----------------------------------------------------

        for percentage in PERCENTAGES:

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


            selected_faults = set(

                shuffled_faults[
                    :k
                ]

            )


            hard_found = len(

                selected_faults
                &
                hard_set

            )


            if hard_count > 0:

                recall = (

                    hard_found
                    /
                    hard_count

                )

            else:

                recall = 0.0


            accumulated_recall[
                percentage
            ] += recall


    # ========================================================
    # 8. AVERAGE RESULTS
    # ========================================================

    average_recall = {}


    for percentage in PERCENTAGES:

        average_recall[
            percentage
        ] = (

            accumulated_recall[
                percentage
            ]
            /
            REPETITIONS

        )


        print()

        print(

            f"Random top {percentage}% "
            f"Hard-fault recall:",

            f"{average_recall[percentage] * 100:.2f}%"

        )


    # ========================================================
    # 9. SAVE BENCHMARK RESULT
    # ========================================================

    all_results.append({

        "benchmark":
            benchmark,

        "total_faults":
            total_faults,

        "relative_hard_faults":
            hard_count,

        "repetitions":
            REPETITIONS,

        "average_hard_fault_recall":
            average_recall

    })


# ============================================================
# 10. SAVE COMPLETE RESULT
# ============================================================

final_result = {

    "experiment":
        "Relative random fault prioritization baseline",

    "target":
        "relative_difficulty",

    "label_definition": {

        "Hard":
            "bottom 25 percent detection count within each benchmark",

        "Medium":
            "middle 50 percent detection count within each benchmark",

        "Easy":
            "top 25 percent detection count within each benchmark"

    },

    "repetitions":
        REPETITIONS,

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
# 11. FINAL SUMMARY
# ============================================================

print()

print(
    "========================================"
)

print(
    "RELATIVE RANDOM BASELINE COMPLETE"
)

print(
    "========================================"
)


for result in all_results:

    benchmark = result[
        "benchmark"
    ]


    print()

    print(
        "Held-out:",
        benchmark.upper()
    )


    recall = result[
        "average_hard_fault_recall"
    ]


    for percentage in PERCENTAGES:

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

print()

print(
    "Experiment complete."
)