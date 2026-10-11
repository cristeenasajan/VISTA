import json
from pathlib import Path

import numpy as np

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    balanced_accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# VISTA RELATIVE-DIFFICULTY CROSS-BENCHMARK ML
# ============================================================
#
# Training strategy:
#
#   C17 + C432  -> C499
#   C17 + C499  -> C432
#   C432 + C499 -> C17
#
# This is Leave-One-Benchmark-Out evaluation.
#
# IMPORTANT:
# detection_count is NOT used as an ML feature.
#
# It was used only to create the relative difficulty label.
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
    / "relative_cross_benchmark_ml_results.json"
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
# 3. CLASS LABELS
# ============================================================

CLASS_NAMES = [

    "Hard",

    "Medium",

    "Easy"
]


LABEL_TO_NUMBER = {

    "Hard": 0,

    "Medium": 1,

    "Easy": 2
}


# ============================================================
# 4. CHECK DATASET
# ============================================================

print()

print(
    "VISTA Relative-Difficulty ML"
)

print(
    "============================"
)


if not DATASET_FILE.exists():

    raise FileNotFoundError(

        f"Dataset not found:\n"
        f"{DATASET_FILE}"

    )


# ============================================================
# 5. LOAD DATASET
# ============================================================

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
    "Dataset:",
    DATASET_FILE
)

print(
    "Total samples:",
    len(samples)
)


# ============================================================
# 6. CONVERT DATA TO ARRAYS
# ============================================================

X = []

y = []

benchmarks = []


for sample in samples:

    # --------------------------------------------------------
    # Feature vector
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


    if difficulty not in LABEL_TO_NUMBER:

        raise ValueError(

            f"Unknown difficulty label: "
            f"{difficulty}"

        )


    y.append(

        LABEL_TO_NUMBER[
            difficulty
        ]

    )


    # --------------------------------------------------------
    # Benchmark
    # --------------------------------------------------------

    benchmarks.append(

        sample[
            "benchmark"
        ]

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


# ============================================================
# 7. DISPLAY DATASET INFORMATION
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


print()

print(
    "Features:"
)


for feature in FEATURE_NAMES:

    print(
        " -",
        feature
    )


print()

print(
    "Target:",
    "relative_difficulty"
)


print()

print(
    "Detection count used as feature:",
    False
)


print(
    "Detection ratio used as feature:",
    False
)


# ============================================================
# 8. LEAVE-ONE-BENCHMARK-OUT EXPERIMENT
# ============================================================

experiments = []


for test_benchmark in benchmark_names:

    print()

    print(
        "========================================"
    )

    print(
        "HELD-OUT BENCHMARK:",
        test_benchmark.upper()
    )

    print(
        "========================================"
    )


    # --------------------------------------------------------
    # Test = one entire benchmark
    # Train = all other benchmarks
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


    training_benchmarks = sorted(

        set(

            benchmarks[
                train_mask
            ]

        )

    )


    # --------------------------------------------------------
    # Display split
    # --------------------------------------------------------

    print()

    print(
        "Training benchmarks:",
        training_benchmarks
    )


    print(
        "Training samples:",
        len(X_train)
    )


    print(
        "Test samples:",
        len(X_test)
    )


    # --------------------------------------------------------
    # Training distribution
    # --------------------------------------------------------

    print()

    print(
        "Training class distribution:"
    )


    for class_number, class_name in enumerate(
        CLASS_NAMES
    ):

        count = np.sum(

            y_train
            ==
            class_number

        )


        print(

            " ",
            class_name,
            ":",
            int(count)

        )


    # ========================================================
    # 9. RANDOM FOREST
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
        "Training Random Forest..."
    )


    model.fit(

        X_train,

        y_train

    )


    print(
        "Training complete."
    )


    # ========================================================
    # 10. PREDICTION
    # ========================================================

    predictions = model.predict(

        X_test

    )


    # ========================================================
    # 11. METRICS
    # ========================================================

    balanced_accuracy = (

        balanced_accuracy_score(

            y_test,

            predictions

        )

    )


    macro_f1 = (

        f1_score(

            y_test,

            predictions,

            labels=[
                0,
                1,
                2
            ],

            average="macro",

            zero_division=0

        )

    )


    weighted_f1 = (

        f1_score(

            y_test,

            predictions,

            labels=[
                0,
                1,
                2
            ],

            average="weighted",

            zero_division=0

        )

    )


    # ========================================================
    # 12. CLASSIFICATION REPORT
    # ========================================================

    report = classification_report(

        y_test,

        predictions,

        labels=[
            0,
            1,
            2
        ],

        target_names=CLASS_NAMES,

        output_dict=True,

        zero_division=0

    )


    # ========================================================
    # 13. CONFUSION MATRIX
    # ========================================================

    matrix = confusion_matrix(

        y_test,

        predictions,

        labels=[
            0,
            1,
            2
        ]

    )


    # ========================================================
    # 14. FEATURE IMPORTANCE
    # ========================================================

    importances = (

        model.feature_importances_

    )


    feature_importance = {

        feature:
            float(value)

        for feature, value

        in zip(

            FEATURE_NAMES,

            importances

        )

    }


    # ========================================================
    # 15. PRINT RESULTS
    # ========================================================

    print()

    print(
        "Balanced accuracy:",
        f"{balanced_accuracy:.4f}"
    )


    print(
        "Macro F1:",
        f"{macro_f1:.4f}"
    )


    print(
        "Weighted F1:",
        f"{weighted_f1:.4f}"
    )


    # --------------------------------------------------------
    # Classification report
    # --------------------------------------------------------

    print()

    print(
        "Classification report:"
    )


    for class_name in CLASS_NAMES:

        class_result = report[
            class_name
        ]


        print(

            class_name,

            "->",

            "Precision:",
            f"{class_result['precision']:.3f}",

            "Recall:",
            f"{class_result['recall']:.3f}",

            "F1:",
            f"{class_result['f1-score']:.3f}",

            "Support:",
            int(class_result["support"])

        )


    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    print()

    print(
        "Confusion matrix:"
    )

    print()

    print(
        "Rows    = actual"
    )

    print(
        "Columns = predicted"
    )

    print()

    print(
        matrix
    )


    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    print()

    print(
        "Feature importance:"
    )


    sorted_features = sorted(

        feature_importance.items(),

        key=lambda item:
            item[1],

        reverse=True

    )


    for feature, importance in sorted_features:

        print(

            f"{feature}: "
            f"{importance:.4f}"

        )


    # ========================================================
    # 16. SAVE EXPERIMENT
    # ========================================================

    experiment = {

        "test_benchmark":
            test_benchmark,

        "training_benchmarks":
            training_benchmarks,

        "training_samples":
            int(
                len(X_train)
            ),

        "test_samples":
            int(
                len(X_test)
            ),

        "balanced_accuracy":
            float(
                balanced_accuracy
            ),

        "macro_f1":
            float(
                macro_f1
            ),

        "weighted_f1":
            float(
                weighted_f1
            ),

        "classification_report":
            report,

        "confusion_matrix":
            matrix.tolist(),

        "feature_importance":
            feature_importance

    }


    experiments.append(
        experiment
    )


# ============================================================
# 17. AVERAGE PERFORMANCE
# ============================================================

balanced_scores = [

    experiment[
        "balanced_accuracy"
    ]

    for experiment in experiments

]


macro_scores = [

    experiment[
        "macro_f1"
    ]

    for experiment in experiments

]


weighted_scores = [

    experiment[
        "weighted_f1"
    ]

    for experiment in experiments

]


average_balanced_accuracy = float(

    np.mean(
        balanced_scores
    )

)


average_macro_f1 = float(

    np.mean(
        macro_scores
    )

)


average_weighted_f1 = float(

    np.mean(
        weighted_scores
    )

)


# ============================================================
# 18. FINAL SUMMARY
# ============================================================

print()

print(
    "========================================"
)

print(
    "RELATIVE CROSS-BENCHMARK SUMMARY"
)

print(
    "========================================"
)


for experiment in experiments:

    print()

    print(

        "Held-out:",
        experiment[
            "test_benchmark"
        ].upper()

    )


    print(

        "Balanced accuracy:",
        f"{experiment['balanced_accuracy']:.4f}"

    )


    print(

        "Macro F1:",
        f"{experiment['macro_f1']:.4f}"

    )


    print(

        "Weighted F1:",
        f"{experiment['weighted_f1']:.4f}"

    )


# ============================================================
# 19. AVERAGES
# ============================================================

print()

print(
    "----------------------------------------"
)


print(

    "Average balanced accuracy:",
    f"{average_balanced_accuracy:.4f}"

)


print(

    "Average macro F1:",
    f"{average_macro_f1:.4f}"

)


print(

    "Average weighted F1:",
    f"{average_weighted_f1:.4f}"

)


# ============================================================
# 20. SAVE RESULTS
# ============================================================

results = {

    "experiment":
        "leave_one_benchmark_out",

    "target":
        "relative_difficulty",

    "feature_type":
        "normalized_structural_features",

    "benchmarks":
        benchmark_names,

    "features":
        FEATURE_NAMES,

    "label_definition": {

        "Hard":
            "bottom 25 percent of detection counts within each benchmark",

        "Medium":
            "middle 50 percent of detection counts within each benchmark",

        "Easy":
            "top 25 percent of detection counts within each benchmark"

    },


    "leakage_check": {

        "detection_count_used":
            False,

        "detection_ratio_used":
            False

    },


    "experiments":
        experiments,


    "average_metrics": {

        "balanced_accuracy":
            average_balanced_accuracy,

        "macro_f1":
            average_macro_f1,

        "weighted_f1":
            average_weighted_f1

    }

}


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
# 21. DONE
# ============================================================

print()

print(
    "Results saved to:"
)

print(
    OUTPUT_FILE
)

print()

print(
    "Cross-benchmark ML experiment complete."
)