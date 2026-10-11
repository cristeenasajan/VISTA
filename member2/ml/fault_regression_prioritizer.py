import json
from pathlib import Path

import numpy as np

from sklearn.ensemble import RandomForestRegressor


# ============================================================
# VISTA ML REGRESSION-BASED FAULT PRIORITIZATION
# ============================================================
#
# Predict:
#
#     detection_rate = detection_count / total_patterns
#
# Detection rate is the TARGET.
#
# Structural features are the ML INPUTS.
#
# IMPORTANT:
# detection_count is NOT used as an input feature.
#
# Evaluation:
#
#     C17  <- train on C432 + C499
#     C432 <- train on C17 + C499
#     C499 <- train on C17 + C432
#
# Lower detection rate = harder fault.
#
# Therefore faults are ranked from LOWEST predicted
# detection rate to HIGHEST predicted detection rate.
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


STRUCTURAL_DATASET = (
    DATA_DIR
    / "multi_benchmark_ml_dataset.json"
)


OUTPUT_FILE = (
    DATA_DIR
    / "ml_regression_prioritization_results.json"
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
# 3. LOAD STRUCTURAL DATA
# ============================================================

print()

print(
    "VISTA ML Regression Fault Prioritization"
)

print(
    "========================================="
)


if not STRUCTURAL_DATASET.exists():

    raise FileNotFoundError(
        f"Structural dataset not found:\n"
        f"{STRUCTURAL_DATASET}\n\n"
        f"Use the existing multi-benchmark dataset."
    )


with open(
    STRUCTURAL_DATASET,
    "r"
) as file:

    dataset_data = json.load(file)


samples = dataset_data["samples"]


print()

print(
    "Structural samples:",
    len(samples)
)


# ============================================================
# 4. LOAD SIMULATION RESULTS
# ============================================================

simulation_results = {}


for benchmark in [

    "c17",
    "c432",
    "c499"

]:

    simulation_file = (

        DATA_DIR
        / f"{benchmark}_simulation_results.json"

    )


    if not simulation_file.exists():

        raise FileNotFoundError(
            f"Simulation results not found:\n"
            f"{simulation_file}"
        )


    with open(
        simulation_file,
        "r"
    ) as file:

        results = json.load(file)


    simulation_results[
        benchmark
    ] = results


    print(

        benchmark.upper(),
        "simulation faults:",
        len(results)

    )


# ============================================================
# 5. CREATE SIMULATION LOOKUP
# ============================================================

simulation_lookup = {}


for benchmark, results in simulation_results.items():

    simulation_lookup[benchmark] = {}


    for fault in results:

        fault_id = str(
            fault["fault_id"]
        )


        simulation_lookup[
            benchmark
        ][
            fault_id
        ] = fault


# ============================================================
# 6. BUILD REGRESSION DATA
# ============================================================

X = []

y = []

benchmarks = []

fault_ids = []

nets = []

fault_types = []

detection_counts = []

pattern_counts = []


missing_simulation = 0


for sample in samples:

    benchmark = sample[
        "benchmark"
    ]


    fault_id = str(
        sample[
            "fault_id"
        ]
    )


    # --------------------------------------------------------
    # Find corresponding simulation result
    # --------------------------------------------------------

    fault = simulation_lookup.get(
        benchmark,
        {}
    ).get(
        fault_id
    )


    if fault is None:

        missing_simulation += 1

        continue


    # --------------------------------------------------------
    # Detection count
    # --------------------------------------------------------

    detection_count = int(

        fault.get(
            "detection_count",
            0
        )

    )


    # --------------------------------------------------------
    # Number of applied patterns
    #
    # C17 uses 32 exhaustive patterns.
    # C432/C499 use 1024 deterministic random patterns.
    # --------------------------------------------------------

    detected_patterns = fault.get(
        "detected_patterns",
        []
    )


    # Every fault result contains the actual number of
    # patterns used through the benchmark simulation setup.
    #
    # Infer from benchmark.
    #

    if benchmark == "c17":

        total_patterns = 32

    else:

        total_patterns = 1024


    # --------------------------------------------------------
    # Detection rate
    # --------------------------------------------------------

    detection_rate = (

        detection_count
        /
        total_patterns

    )


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
    # Regression target
    # --------------------------------------------------------

    y.append(
        detection_rate
    )


    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    benchmarks.append(
        benchmark
    )


    fault_ids.append(
        fault_id
    )


    nets.append(
        sample.get(
            "net",
            ""
        )
    )


    fault_types.append(
        sample.get(
            "fault_type",
            ""
        )
    )


    detection_counts.append(
        detection_count
    )


    pattern_counts.append(
        total_patterns
    )


# ============================================================
# 7. CONVERT TO NUMPY
# ============================================================

X = np.array(
    X,
    dtype=float
)


y = np.array(
    y,
    dtype=float
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


detection_counts = np.array(
    detection_counts
)


pattern_counts = np.array(
    pattern_counts
)


print()

print(
    "Usable regression samples:",
    len(X)
)


print(
    "Missing simulation results:",
    missing_simulation
)


print()

print(
    "Target: detection_rate"
)


print(
    "Detection count used as feature:",
    False
)


# ============================================================
# 8. BENCHMARKS
# ============================================================

benchmark_names = sorted(
    set(
        benchmarks
    )
)


# ============================================================
# 9. RESULTS STORAGE
# ============================================================

all_results = []


# ============================================================
# 10. LEAVE-ONE-BENCHMARK-OUT
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
    # Split
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
    # 11. TRAIN REGRESSOR
    # ========================================================

    model = RandomForestRegressor(

        n_estimators=300,

        random_state=42,

        min_samples_leaf=2,

        n_jobs=-1

    )


    print()

    print(
        "Training Random Forest Regressor..."
    )


    model.fit(
        X_train,
        y_train
    )


    print(
        "Training complete."
    )


    # ========================================================
    # 12. PREDICT DETECTION RATE
    # ========================================================

    predictions = model.predict(
        X_test
    )


    # Keep predictions within physical range.

    predictions = np.clip(
        predictions,
        0.0,
        1.0
    )


    # ========================================================
    # 13. RANK FAULTS
    # ========================================================
    #
    # LOW detection rate means HARD fault.
    #
    # Therefore:
    #
    # lowest predicted detection rate
    #              ↓
    # highest priority
    #
    # ========================================================

    test_indices = np.where(
        test_mask
    )[0]


    ranked_faults = []


    for local_index, original_index in enumerate(
        test_indices
    ):

        predicted_rate = float(
            predictions[
                local_index
            ]
        )


        actual_rate = float(
            y_test[
                local_index
            ]
        )


        detection_count = int(
            detection_counts[
                original_index
            ]
        )


        total_patterns = int(
            pattern_counts[
                original_index
            ]
        )


        # ----------------------------------------------------
        # Actual difficulty
        #
        # Use original VISTA diagnosis threshold here.
        #
        # 0 detections  -> Hard
        # <=8 detections -> Medium
        # >8 detections -> Easy
        #
        # This is ONLY for evaluation.
        # It is NOT an ML feature.
        # ----------------------------------------------------

        if detection_count == 0:

            actual_difficulty = "Hard"

        elif detection_count <= 8:

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

            "predicted_detection_rate":
                predicted_rate,

            "actual_detection_rate":
                actual_rate,

            "detection_count":
                detection_count,

            "total_patterns":
                total_patterns,

            "actual_difficulty":
                actual_difficulty

        })


    # --------------------------------------------------------
    # Sort hardest first
    # --------------------------------------------------------

    ranked_faults.sort(

        key=lambda fault:
            fault[
                "predicted_detection_rate"
            ]

    )


    # ========================================================
    # 14. HARD FAULT ANALYSIS
    # ========================================================

    actual_hard_faults = [

        fault

        for fault in ranked_faults

        if fault[
            "actual_difficulty"
        ]
        ==
        "Hard"

    ]


    total_faults = len(
        ranked_faults
    )


    hard_count = len(
        actual_hard_faults
    )


    print()

    print(
        "Total faults:",
        total_faults
    )


    print(
        "Actual Hard faults:",
        hard_count
    )


    priority_metrics = {}


    # ========================================================
    # 15. TOP 10 / 20 / 30 PERCENT
    # ========================================================

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
            hard_count

            if hard_count > 0

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
                hard_count,

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
    # 16. TOP 10 FAULTS
    # ========================================================

    print()

    print(
        "Top 10 regression-prioritized faults:"
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
            f"| PredRate="
            f"{fault['predicted_detection_rate']:.4f} "
            f"| ActualRate="
            f"{fault['actual_detection_rate']:.4f} "
            f"| Actual="
            f"{fault['actual_difficulty']}"

        )


    # ========================================================
    # 17. FEATURE IMPORTANCE
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
    # 18. SAVE BENCHMARK RESULT
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

        "hard_faults":
            hard_count,

        "priority_metrics":
            priority_metrics,

        "feature_importance":
            feature_importance,

        "ranked_faults":
            ranked_faults

    }


    all_results.append(
        benchmark_result
    )


# ============================================================
# 19. SAVE FINAL RESULTS
# ============================================================

final_result = {

    "experiment":
        "Regression-based ML fault prioritization",

    "evaluation":
        "leave-one-benchmark-out",

    "target":
        "detection_rate",

    "features":
        FEATURE_NAMES,

    "results":
        all_results,

    "leakage_check": {

        "detection_count_used_as_feature":
            False,

        "detection_rate_used_as_feature":
            False

    }

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
# 20. FINAL SUMMARY
# ============================================================

print()

print(
    "========================================"
)

print(
    "REGRESSION PRIORITIZATION COMPLETE"
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


print()

print(
    "Regression experiment complete."
)