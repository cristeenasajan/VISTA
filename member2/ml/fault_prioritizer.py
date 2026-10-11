import json
from pathlib import Path

import numpy as np

from sklearn.ensemble import RandomForestClassifier


# ============================================================
# VISTA ML-GUIDED FAULT PRIORITIZATION
# ============================================================
#
# Goal:
#
# Use structural RTL features to predict which faults are
# likely to be difficult.
#
# Then prioritize those faults for earlier testing.
#
# Evaluation:
#
#   C17  -> trained on C432 + C499
#   C432 -> trained on C17 + C499
#   C499 -> trained on C17 + C432
#
# This is leave-one-benchmark-out evaluation.
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


DATASET_FILE = (
    DATA_DIR
    / "relative_multi_benchmark_ml_dataset.json"
)


OUTPUT_FILE = (
    DATA_DIR
    / "ml_fault_prioritization_results.json"
)


# ============================================================
# 2. FEATURES
# ============================================================

FEATURE_NAMES = [

    "is_sa0",

    "is_sa1",

    "is_primary_input",

    "is_primary_output",

    "is_internal",

    "gate_type",

    "normalized_fanin",

    "normalized_fanout",

    "normalized_logic_depth",

    "normalized_distance_to_output"

]


# ============================================================
# 3. LOAD DATASET
# ============================================================

print()

print(
    "VISTA ML-Guided Fault Prioritization"
)

print(
    "====================================="
)


if not DATASET_FILE.exists():

    raise FileNotFoundError(

        f"Dataset not found:\n"
        f"{DATASET_FILE}"

    )


with open(
    DATASET_FILE,
    "r"
) as file:

    dataset_data = json.load(
        file
    )


samples = dataset_data[
    "samples"
]


print()

print(
    "Total samples:",
    len(samples)
)


# ============================================================
# 4. CONVERT DATA
# ============================================================

X = []

y = []

benchmarks = []

fault_ids = []

nets = []

fault_types = []


LABEL_TO_NUMBER = {

    "Hard": 0,

    "Medium": 1,

    "Easy": 2

}


for sample in samples:

    # --------------------------------------------------------
    # Features
    # --------------------------------------------------------

    feature_vector = []

    for feature in FEATURE_NAMES:

        feature_vector.append(

            float(
                sample.get(
                    feature,
                    0
                )
            )

        )


    X.append(
        feature_vector
    )


    # --------------------------------------------------------
    # Target
    # --------------------------------------------------------

    difficulty = sample[
        "difficulty"
    ]


    y.append(

        LABEL_TO_NUMBER[
            difficulty
        ]

    )


    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    benchmarks.append(
        sample["benchmark"]
    )


    fault_ids.append(
        sample["fault_id"]
    )


    nets.append(
        sample["net"]
    )


    # Some datasets may not contain fault_type.
    # Keep it safe.

    fault_types.append(

        sample.get(
            "fault_type",
            ""
        )

    )


X = np.array(
    X,
    dtype=float
)


y = np.array(
    y,
    dtype=int
)


benchmarks = np.array(
    benchmarks
)


fault_ids = np.array(
    fault_ids
)


nets = np.array(
    nets
)


fault_types = np.array(
    fault_types
)


# ============================================================
# 5. BENCHMARKS
# ============================================================

benchmark_names = sorted(

    set(
        benchmarks
    )

)


print()

print(
    "Benchmarks:",
    benchmark_names
)


# ============================================================
# 6. RESULTS STORAGE
# ============================================================

all_results = []


# ============================================================
# 7. LEAVE-ONE-BENCHMARK-OUT
# ============================================================

for test_benchmark in benchmark_names:

    print()

    print(
        "========================================"
    )

    print(
        "HELD-OUT:",
        test_benchmark.upper()
    )

    print(
        "========================================"
    )


    # --------------------------------------------------------
    # Train / test split
    # --------------------------------------------------------

    test_mask = (

        benchmarks
        ==
        test_benchmark

    )


    train_mask = (

        benchmarks
        !=
        test_benchmark

    )


    X_train = X[
        train_mask
    ]


    y_train = y[
        train_mask
    ]


    X_test = X[
        test_mask
    ]


    y_test = y[
        test_mask
    ]


    print()

    print(
        "Training samples:",
        len(X_train)
    )


    print(
        "Test samples:",
        len(X_test)
    )


    # ========================================================
    # 8. TRAIN RANDOM FOREST
    # ========================================================

    model = RandomForestClassifier(

        n_estimators=300,

        random_state=42,

        class_weight="balanced",

        min_samples_leaf=2,

        n_jobs=-1

    )


    print()

    print(
        "Training model..."
    )


    model.fit(

        X_train,

        y_train

    )


    print(
        "Model trained."
    )


    # ========================================================
    # 9. PREDICT CLASS
    # ========================================================

    predictions = model.predict(
        X_test
    )


    # ========================================================
    # 10. PREDICT PROBABILITIES
    # ========================================================
    #
    # Probability columns correspond to model.classes_.
    #
    # We specifically want:
    #
    # P(Hard)
    #
    # ========================================================

    probabilities = model.predict_proba(
        X_test
    )


    class_to_column = {

        class_number: index

        for index, class_number

        in enumerate(
            model.classes_
        )

    }


    hard_column = class_to_column.get(
        0
    )


    medium_column = class_to_column.get(
        1
    )


    easy_column = class_to_column.get(
        2
    )


    # ========================================================
    # 11. BUILD FAULT RECORDS
    # ========================================================

    test_indices = np.where(
        test_mask
    )[0]


    ranked_faults = []


    for local_index, original_index in enumerate(
        test_indices
    ):

        hard_probability = (

            float(
                probabilities[
                    local_index,
                    hard_column
                ]
            )

            if hard_column is not None

            else 0.0

        )


        medium_probability = (

            float(
                probabilities[
                    local_index,
                    medium_column
                ]
            )

            if medium_column is not None

            else 0.0

        )


        easy_probability = (

            float(
                probabilities[
                    local_index,
                    easy_column
                ]
            )

            if easy_column is not None

            else 0.0

        )


        predicted_class = int(

            predictions[
                local_index
            ]

        )


        if predicted_class == 0:

            predicted_difficulty = "Hard"

        elif predicted_class == 1:

            predicted_difficulty = "Medium"

        else:

            predicted_difficulty = "Easy"


        actual_class = int(

            y_test[
                local_index
            ]

        )


        if actual_class == 0:

            actual_difficulty = "Hard"

        elif actual_class == 1:

            actual_difficulty = "Medium"

        else:

            actual_difficulty = "Easy"


        ranked_faults.append({

            "benchmark":
                test_benchmark,

            "fault_id":
                str(
                    fault_ids[
                        original_index
                    ]
                ),

            "net":
                str(
                    nets[
                        original_index
                    ]
                ),

            "fault_type":
                str(
                    fault_types[
                        original_index
                    ]
                ),

            "predicted_difficulty":
                predicted_difficulty,

            "actual_difficulty":
                actual_difficulty,

            "hard_probability":
                hard_probability,

            "medium_probability":
                medium_probability,

            "easy_probability":
                easy_probability

        })


    # ========================================================
    # 12. RANK BY HARD PROBABILITY
    # ========================================================

    ranked_faults.sort(

        key=lambda fault:
            fault[
                "hard_probability"
            ],

        reverse=True

    )


    # ========================================================
    # 13. TOP-K ANALYSIS
    # ========================================================
    #
    # Question:
    #
    # If we test the highest-priority faults first,
    # how many actual Hard faults do we encounter?
    #
    # ========================================================

    total_faults = len(
        ranked_faults
    )


    actual_hard_faults = sum(

        1

        for fault in ranked_faults

        if fault[
            "actual_difficulty"
        ]
        ==
        "Hard"

    )


    print()

    print(
        "Total faults:",
        total_faults
    )


    print(
        "Actual Hard faults:",
        actual_hard_faults
    )


    priority_metrics = {}


    for percentage in [

        10,

        20,

        30

    ]:

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


        top_faults = ranked_faults[
            :k
        ]


        hard_found = sum(

            1

            for fault in top_faults

            if fault[
                "actual_difficulty"
            ]
            ==
            "Hard"

        )


        hard_recall = (

            hard_found
            /
            actual_hard_faults

            if actual_hard_faults > 0

            else 0.0

        )


        random_expected = (

            percentage
            /
            100.0

        )


        priority_metrics[
            f"top_{percentage}_percent"
        ] = {

            "faults_tested":
                k,

            "hard_faults_found":
                hard_found,

            "total_hard_faults":
                actual_hard_faults,

            "hard_recall":
                float(
                    hard_recall
                ),

            "random_expected_recall":
                random_expected

        }


        print()

        print(
            f"Top {percentage}%:"
        )


        print(

            "  Faults tested:",
            k

        )


        print(

            "  Hard faults found:",
            hard_found

        )


        print(

            "  Hard-fault recall:",
            f"{hard_recall * 100:.2f}%"

        )


        print(

            "  Random expected:",
            f"{random_expected * 100:.2f}%"

        )


    # ========================================================
    # 14. PRINT TOP 10
    # ========================================================

    print()

    print(
        "Top 10 prioritized faults:"
    )


    for rank, fault in enumerate(

        ranked_faults[
            :10
        ],

        start=1

    ):

        print(

            f"{rank:2d}. "
            f"{fault['fault_id']} "
            f"-> {fault['net']} "
            f"{fault['fault_type']} "
            f"| Hard P="
            f"{fault['hard_probability']:.3f} "
            f"| Actual="
            f"{fault['actual_difficulty']}"

        )


    # ========================================================
    # 15. SAVE THIS BENCHMARK RESULT
    # ========================================================

    benchmark_result = {

        "held_out_benchmark":
            test_benchmark,

        "training_benchmarks":
            sorted(

                set(
                    benchmarks[
                        train_mask
                    ]
                )

            ),

        "total_faults":
            total_faults,

        "actual_hard_faults":
            actual_hard_faults,

        "priority_metrics":
            priority_metrics,

        "ranked_faults":
            ranked_faults

    }


    all_results.append(
        benchmark_result
    )


# ============================================================
# 16. SAVE COMPLETE RESULTS
# ============================================================

final_result = {

    "experiment":
        "ML-guided fault prioritization",

    "evaluation":
        "leave-one-benchmark-out",

    "ranking_target":
        "predicted probability of Hard difficulty",

    "features":
        FEATURE_NAMES,

    "benchmarks":
        benchmark_names,

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
# 17. FINAL SUMMARY
# ============================================================

print()

print(
    "========================================"
)

print(
    "ML PRIORITIZATION COMPLETE"
)

print(
    "========================================"
)


for result in all_results:

    benchmark = result[
        "held_out_benchmark"
    ]


    print()

    print(
        "Held-out:",
        benchmark.upper()
    )


    for percentage in [

        10,

        20,

        30

    ]:

        metrics = result[
            "priority_metrics"
        ][
            f"top_{percentage}_percent"
        ]


        print(

            f"Top {percentage}% -> "
            f"{metrics['hard_recall'] * 100:.2f}% "
            f"Hard-fault recall"

        )


print()

print(
    "Results saved to:"
)

print(
    OUTPUT_FILE
)