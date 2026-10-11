import json
from pathlib import Path


# ============================================================
# VISTA RELATIVE-DIFFICULTY ML DATASET
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = (
    BASE_DIR
    / "member2"
    / "data"
)

BENCHMARKS = [
    "c17",
    "c432",
    "c499"
]


# ============================================================
# LOAD JSON
# ============================================================

def load_json(filename):

    filepath = DATA_DIR / filename

    if not filepath.exists():

        raise FileNotFoundError(
            f"File not found:\n{filepath}"
        )

    with open(filepath, "r") as file:

        return json.load(file)


# ============================================================
# SAFE INTEGER
# ============================================================

def safe_int(value):

    try:
        return int(value)

    except (
        TypeError,
        ValueError
    ):

        return 0


# ============================================================
# GATE TYPE ENCODING
# ============================================================

GATE_TYPES = {

    "unknown": 0,

    "and": 1,
    "or": 2,
    "nand": 3,
    "nor": 4,

    "xor": 5,
    "xnor": 6,

    "not": 7,
    "buf": 8,

    "input": 9,
    "output": 10
}


def encode_gate_type(gate_type):

    if gate_type is None:

        return 0

    gate = str(
        gate_type
    ).lower().strip()

    return GATE_TYPES.get(
        gate,
        0
    )


# ============================================================
# NET TYPE FLAGS
# ============================================================

def get_net_type_flags(net_type):

    net_type = str(
        net_type
    ).lower().strip()


    return (

        1 if net_type == "primary_input" else 0,

        1 if net_type == "primary_output" else 0,

        1 if net_type == "internal" else 0

    )


# ============================================================
# LOAD STRUCTURAL FEATURES
# ============================================================

def load_structural_features(
    benchmark
):

    data = load_json(

        f"{benchmark}_structural_features.json"

    )


    features = data.get(
        "features",
        []
    )


    structural_map = {}


    for item in features:

        if not isinstance(
            item,
            dict
        ):

            continue


        net = item.get(
            "net"
        )


        if net is not None:

            structural_map[
                str(net)
            ] = item


    return structural_map


# ============================================================
# CREATE RELATIVE LABELS
# ============================================================

def create_relative_labels(
    simulation_results
):

    # --------------------------------------------------------
    # Get detection counts
    # --------------------------------------------------------

    detection_counts = [

        safe_int(
            fault.get(
                "detection_count"
            )
        )

        for fault in simulation_results

    ]


    if not detection_counts:

        return []


    # --------------------------------------------------------
    # Sort detection counts
    # --------------------------------------------------------

    sorted_counts = sorted(
        detection_counts
    )


    total = len(
        sorted_counts
    )


    # --------------------------------------------------------
    # Use percentile-based labels
    #
    # Bottom 25%  -> Hard
    # Middle 50%  -> Medium
    # Top 25%     -> Easy
    #
    # This is benchmark-relative.
    # --------------------------------------------------------

    hard_index = max(
        0,
        int(
            total * 0.25
        ) - 1
    )


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
# PROCESS BENCHMARK
# ============================================================

def process_benchmark(
    benchmark
):

    print()
    print(
        "Processing:",
        benchmark.upper()
    )

    print(
        "------------------------"
    )


    # --------------------------------------------------------
    # Simulation results
    # --------------------------------------------------------

    simulation_results = load_json(

        f"{benchmark}_simulation_results.json"

    )


    print(
        "Simulation faults:",
        len(
            simulation_results
        )
    )


    # --------------------------------------------------------
    # Structural features
    # --------------------------------------------------------

    structural_map = (
        load_structural_features(
            benchmark
        )
    )


    print(
        "Structural nets:",
        len(
            structural_map
        )
    )


    # --------------------------------------------------------
    # Maximum values for normalization
    # --------------------------------------------------------

    max_fanin = 1

    max_fanout = 1

    max_logic_depth = 1

    max_distance = 1


    for item in structural_map.values():

        max_fanin = max(
            max_fanin,
            safe_int(
                item.get(
                    "fanin"
                )
            )
        )


        max_fanout = max(
            max_fanout,
            safe_int(
                item.get(
                    "fanout"
                )
            )
        )


        max_logic_depth = max(
            max_logic_depth,
            safe_int(
                item.get(
                    "logic_depth"
                )
            )
        )


        max_distance = max(
            max_distance,
            safe_int(
                item.get(
                    "distance_to_output"
                )
            )
        )


    # --------------------------------------------------------
    # Create relative labels
    # --------------------------------------------------------

    relative_labels = create_relative_labels(
        simulation_results
    )


    dataset = []

    missing = 0


    # ========================================================
    # BUILD SAMPLES
    # ========================================================

    for index, fault in enumerate(
        simulation_results
    ):

        net = fault.get(
            "net"
        )


        structural = structural_map.get(
            str(net)
        )


        if structural is None:

            missing += 1

            continue


        # ----------------------------------------------------
        # Relative label
        # ----------------------------------------------------

        difficulty = relative_labels[
            index
        ]


        # ----------------------------------------------------
        # Fault type
        # ----------------------------------------------------

        fault_type = fault.get(
            "fault_type"
        )


        is_sa0 = (

            1
            if fault_type == "SA0"
            else 0

        )


        is_sa1 = (

            1
            if fault_type == "SA1"
            else 0

        )


        # ----------------------------------------------------
        # Net type
        # ----------------------------------------------------

        (
            is_primary_input,
            is_primary_output,
            is_internal

        ) = get_net_type_flags(

            structural.get(
                "net_type"
            )

        )


        # ----------------------------------------------------
        # Structural values
        # ----------------------------------------------------

        fanin = safe_int(
            structural.get(
                "fanin"
            )
        )


        fanout = safe_int(
            structural.get(
                "fanout"
            )
        )


        logic_depth = safe_int(
            structural.get(
                "logic_depth"
            )
        )


        distance_to_output = safe_int(
            structural.get(
                "distance_to_output"
            )
        )


        # ----------------------------------------------------
        # Normalize
        # ----------------------------------------------------

        normalized_fanin = (
            fanin
            /
            max_fanin
        )


        normalized_fanout = (
            fanout
            /
            max_fanout
        )


        normalized_logic_depth = (
            logic_depth
            /
            max_logic_depth
        )


        normalized_distance_to_output = (
            distance_to_output
            /
            max_distance
        )


        # ----------------------------------------------------
        # Gate type
        # ----------------------------------------------------

        gate_type = encode_gate_type(

            structural.get(
                "gate_type"
            )

        )


        # ====================================================
        # CREATE SAMPLE
        # ====================================================

        sample = {

            "benchmark":
                benchmark,

            "fault_id":
                fault.get(
                    "fault_id"
                ),

            "net":
                net,


            "is_sa0":
                is_sa0,

            "is_sa1":
                is_sa1,


            "is_primary_input":
                is_primary_input,

            "is_primary_output":
                is_primary_output,

            "is_internal":
                is_internal,


            "gate_type":
                gate_type,


            "normalized_fanin":
                normalized_fanin,

            "normalized_fanout":
                normalized_fanout,

            "normalized_logic_depth":
                normalized_logic_depth,

            "normalized_distance_to_output":
                normalized_distance_to_output,


            # -----------------------------------------------
            # IMPORTANT:
            # Detection count is NOT an ML feature.
            # It is only used to create the target label.
            # -----------------------------------------------

            "difficulty":
                difficulty
        }


        dataset.append(
            sample
        )


    # ========================================================
    # CLASS DISTRIBUTION
    # ========================================================

    hard = 0

    medium = 0

    easy = 0


    for sample in dataset:

        if sample[
            "difficulty"
        ] == "Hard":

            hard += 1

        elif sample[
            "difficulty"
        ] == "Medium":

            medium += 1

        elif sample[
            "difficulty"
        ] == "Easy":

            easy += 1


    print()
    print(
        "Hard:",
        hard
    )

    print(
        "Medium:",
        medium
    )

    print(
        "Easy:",
        easy
    )


    print()
    print(
        "Usable samples:",
        len(dataset)
    )

    print(
        "Missing structural features:",
        missing
    )


    return dataset


# ============================================================
# BUILD COMPLETE DATASET
# ============================================================

print()
print(
    "VISTA Relative-Difficulty ML Dataset"
)

print(
    "====================================="
)


all_samples = []


for benchmark in BENCHMARKS:

    samples = process_benchmark(
        benchmark
    )

    all_samples.extend(
        samples
    )


# ============================================================
# FEATURE LIST
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
# SAVE
# ============================================================

OUTPUT_FILE = (

    DATA_DIR
    /
    "relative_multi_benchmark_ml_dataset.json"

)


result = {

    "benchmarks":
        BENCHMARKS,

    "total_samples":
        len(all_samples),

    "features":
        FEATURE_NAMES,

    "target":
        "relative_difficulty",

    "label_definition": {

        "Hard":
            "bottom 25 percent of detection counts within each benchmark",

        "Medium":
            "middle 50 percent of detection counts within each benchmark",

        "Easy":
            "top 25 percent of detection counts within each benchmark"
    },


    "leakage_check": {

        "detection_count_used_as_feature":
            False,

        "detection_ratio_used_as_feature":
            False
    },


    "samples":
        all_samples
}


with open(
    OUTPUT_FILE,
    "w"
) as file:

    json.dump(
        result,
        file,
        indent=4
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print(
    "====================================="
)

print(
    "Dataset creation complete"
)

print(
    "====================================="
)


print()
print(
    "Total samples:",
    len(all_samples)
)


hard_total = sum(
    1
    for sample in all_samples
    if sample["difficulty"] == "Hard"
)


medium_total = sum(
    1
    for sample in all_samples
    if sample["difficulty"] == "Medium"
)


easy_total = sum(
    1
    for sample in all_samples
    if sample["difficulty"] == "Easy"
)


print(
    "Hard:",
    hard_total
)

print(
    "Medium:",
    medium_total
)

print(
    "Easy:",
    easy_total
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


print()
print(
    "Dataset saved to:"
)

print(
    OUTPUT_FILE
)