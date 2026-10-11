import json
from pathlib import Path


# ============================================================
# VISTA ML vs RANDOM FAULT PRIORITIZATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "member2" / "data"

ML_FILE = (
    DATA_DIR
    / "ml_fault_prioritization_results.json"
)

RANDOM_FILE = (
    DATA_DIR
    / "random_relative_baseline_results.json"
)

OUTPUT_FILE = (
    DATA_DIR
    / "ml_vs_random_comparison.json"
)


# ============================================================
# LOAD RESULTS
# ============================================================

with open(
    ML_FILE,
    "r"
) as file:

    ml_data = json.load(file)


with open(
    RANDOM_FILE,
    "r"
) as file:

    random_data = json.load(file)


# ============================================================
# BUILD LOOKUPS
# ============================================================

ml_results = {

    result["held_out_benchmark"]:
        result

    for result in ml_data["results"]

}


random_results = {

    result["benchmark"]:
        result

    for result in random_data["results"]

}


# ============================================================
# COMPARISON
# ============================================================

benchmarks = [
    "c17",
    "c432",
    "c499"
]


comparison = []


print()
print(
    "VISTA ML vs RANDOM PRIORITIZATION"
)

print(
    "================================="
)


for benchmark in benchmarks:

    ml_result = ml_results[
        benchmark
    ]

    random_result = random_results[
        benchmark
    ]


    print()
    print(
        "Benchmark:",
        benchmark.upper()
    )

    print(
        "-" * 40
    )


    benchmark_comparison = {

        "benchmark":
            benchmark,

        "budgets": {}

    }


    for percentage in [
        10,
        20,
        30
    ]:

        key = (
            f"top_{percentage}_percent"
        )


        # ----------------------------------------------------
        # ML result
        # ----------------------------------------------------

        ml_recall = (

            ml_result[
                "priority_metrics"
            ][
                key
            ][
                "hard_recall"
            ]

        )


        # ----------------------------------------------------
        # Random result
        # ----------------------------------------------------

        random_recall = (

            random_result[
                "average_hard_fault_recall"
            ][
                str(percentage)
            ]

        )


        # ----------------------------------------------------
        # Absolute improvement
        # ----------------------------------------------------

        absolute_improvement = (

            ml_recall
            -
            random_recall

        )


        # ----------------------------------------------------
        # Relative improvement
        #
        # Example:
        #
        # ML = 40%
        # Random = 20%
        #
        # Relative improvement =
        # (40 - 20) / 20 = 100%
        # ----------------------------------------------------

        if random_recall > 0:

            relative_improvement = (

                absolute_improvement
                /
                random_recall

            )

        else:

            relative_improvement = 0.0


        # ----------------------------------------------------
        # Determine winner
        # ----------------------------------------------------

        if ml_recall > random_recall:

            winner = "ML"

        elif ml_recall < random_recall:

            winner = "Random"

        else:

            winner = "Tie"


        benchmark_comparison[
            "budgets"
        ][
            str(percentage)
        ] = {

            "ml_hard_recall":
                ml_recall,

            "random_hard_recall":
                random_recall,

            "absolute_improvement":
                absolute_improvement,

            "relative_improvement":
                relative_improvement,

            "winner":
                winner

        }


        print()

        print(
            f"Top {percentage}%"
        )

        print(
            f"  ML     : "
            f"{ml_recall * 100:.2f}%"
        )

        print(
            f"  Random : "
            f"{random_recall * 100:.2f}%"
        )

        print(
            f"  Change : "
            f"{absolute_improvement * 100:+.2f} percentage points"
        )

        print(
            f"  Relative: "
            f"{relative_improvement * 100:+.2f}%"
        )

        print(
            f"  Winner : "
            f"{winner}"
        )


    comparison.append(
        benchmark_comparison
    )


# ============================================================
# OVERALL SUMMARY
# ============================================================

print()
print(
    "================================="
)

print(
    "OVERALL SUMMARY"
)

print(
    "================================="
)


ml_wins = 0
random_wins = 0
ties = 0


for result in comparison:

    benchmark = result[
        "benchmark"
    ]


    for percentage in [
        10,
        20,
        30
    ]:

        winner = result[
            "budgets"
        ][
            str(percentage)
        ][
            "winner"
        ]


        if winner == "ML":

            ml_wins += 1

        elif winner == "Random":

            random_wins += 1

        else:

            ties += 1


print(
    "ML wins:",
    ml_wins
)

print(
    "Random wins:",
    random_wins
)

print(
    "Ties:",
    ties
)


# ============================================================
# SAVE
# ============================================================

final_result = {

    "experiment":
        "ML vs Random fault prioritization",

    "comparison_basis":
        "relative Hard-fault recall",

    "benchmarks":
        benchmarks,

    "budgets":
        [
            10,
            20,
            30
        ],

    "summary": {

        "ml_wins":
            ml_wins,

        "random_wins":
            random_wins,

        "ties":
            ties

    },

    "results":
        comparison

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


print()

print(
    "Comparison saved to:"
)

print(
    OUTPUT_FILE
)

print()

print(
    "ML vs Random comparison complete."
)