# VISTA --- Verification Intelligence & Silicon Test Analyzer

VISTA is a software-based VLSI testing and analysis platform designed to
analyze RTL benchmarks, simulate stuck-at faults, evaluate fault
coverage, diagnose faults, compact test patterns, and explore
machine-learning-assisted test intelligence.

The project combines conventional digital test techniques with data
analysis and an experimental machine-learning pipeline.

## 1. Project Objectives

-   Analyze Verilog RTL benchmarks.
-   Generate and simulate stuck-at faults.
-   Measure fault detection and coverage.
-   Diagnose detected and undetected faults.
-   Reduce test-pattern count while preserving detectable-fault
    coverage.
-   Extract structural features from RTL.
-   Evaluate machine-learning-based fault-difficulty classification.
-   Present benchmark and analysis results through a dashboard.
-   Integrate ATPG and test-analysis results from separate project
    components.

## 2. Architecture

``` text
RTL Verilog Benchmarks
        |
        v
RTL Analysis and Structural Features
        |
        v
Fault Generation and Injection
        |
        v
Golden and Faulty Circuit Simulation
        |
        v
Fault Coverage and Diagnosis
        |
        v
Test-Pattern Compaction
        |
        v
Structural Feature Extraction and ML
        |
        v
Dashboard and Experimental Analysis
```

The project includes separate components for RTL analysis, fault
simulation, coverage analysis, diagnosis, optimization, machine
learning, experiments, and visualization.

## 3. Technology Stack

-   **Programming languages:** Python, Verilog
-   **Simulation:** Icarus Verilog and VVP
-   **RTL analysis:** PyVerilog and custom structural-analysis utilities
-   **Data processing:** JSON, NumPy, Pandas
-   **Machine learning:** scikit-learn
-   **Testing:** pytest
-   **Visualization:** Streamlit
-   **Development environment:** Windows, Python virtual environment,
    MSYS2 UCRT64
-   **Version control:** Git

## 4. Repository Structure

``` text
VISTA/
├── benchmarks/
├── docs/
├── member2/
│   ├── coverage/
│   ├── dashboard/
│   ├── diagnosis/
│   ├── experiments/
│   ├── ml/
│   ├── optimisation/
│   ├── optimization/
│   ├── rtl/
│   ├── simulation/
│   ├── tests/
│   ├── data/
│   └── dashboard.py
├── member 1/
├── .venv/
├── requirements.txt
└── README.md
```

The project also uses a separate Member 1 checkout for the C499
integration workflow.

The `optimisation` and `optimization` directories are both present in
the current working project. Review their contents before consolidating
or renaming either directory.

## 5. Verified Benchmark Results

### 5.1 C17

  Metric                            Result
  ------------------------------- --------
  Primary inputs                         5
  Primary outputs                        2
  Logic gates                            6
  Generated stuck-at faults             22
  Successfully simulated faults         22
  Detected faults                       22
  Total fault coverage                100%
  Original patterns                     32
  Compacted patterns                     4
  Pattern-count reduction           87.50%

The C17 simulator processed all 22 faults successfully, with no
simulation failures.

### 5.2 C432

  Metric                        Result
  --------------------------- --------
  Primary inputs                    36
  Primary outputs                    7
  Internal nets                    164
  Logic gates                      171
  Generated stuck-at faults        414
  Detected faults                  411
  Undetected faults                  3
  Total fault coverage          99.28%
  Original patterns              1,024
  Compacted patterns                18
  Pattern-count reduction       98.24%

The C432 simulation used 1,024 deterministic random patterns. Compaction
retained coverage of all 411 faults detected by the original pattern
set.

The three faults not detected by the original pattern set were:

-   F200: N259 SA1
-   F292: N347 SA1
-   F330: N379 SA1

These results do not establish that the three faults are redundant.

### 5.3 C499

  Metric                                     Result
  --------------------------------------- ---------
  Generated stuck-at faults                     758
  Originally detectable faults                  750
  Undetected faults                               8
  Total fault coverage                       98.94%
  Original patterns                             138
  Compacted patterns                             75
  Pattern-count reduction                    45.65%
  Originally detectable faults retained     750/750

The C499 integration adapts Member 1's schema-version-1.1 detection
matrix to Member 2's pattern-compaction workflow.

The reduced pattern set was converted into a new ATPG report and
evaluated using a fresh detection-matrix run. The latest standard
workflow confirmed that all 750 originally detectable faults remained
covered.

The eight faults not detected by the original pattern set are:

-   354 -\> 597.0 / SA1
-   367 -\> 596.1 / SA1
-   380 -\> 595.2 / SA1
-   393 -\> 594.3 / SA1
-   406 -\> 601.0 / SA1
-   419 -\> 600.1 / SA1
-   432 -\> 599.2 / SA1
-   445 -\> 598.3 / SA1

The standard workflow skips independent reference verification to reduce
execution time. A separate earlier run reported agreement with the
reference simulator; independent reference verification was not
performed during the latest standard run.

### Coverage definitions

**Total fault coverage** is the number of detected faults divided by the
total number of modeled faults.

**Coverage of originally detectable faults** is the number of originally
detectable faults retained by the compacted set divided by the number
detected by the original set.

These metrics are different. Preserving coverage of originally
detectable faults does not imply 100% coverage of the complete fault
universe.

Pattern-count reduction alone does not demonstrate reduced physical test
time, silicon area, power, or manufacturing cost.

## 6. Machine-Learning Prototype

The ML prototype evaluates structural features associated with
fault-difficulty classification on C432.

### Features

The current feature set includes:

-   Fault polarity: SA0 or SA1
-   Primary-input, primary-output, or internal-net category
-   Gate type
-   Fan-in
-   Fan-out
-   Logic depth
-   Distance to a primary output

The current dataset contains 414 fault samples.

### Recorded evaluation results

  Metric                    Result
  ----------------------- --------
  Total dataset samples        414
  Test samples                 104
  Test accuracy             93.27%
  Balanced accuracy         97.69%
  Macro F1-score            63.62%

The dataset is severely imbalanced:

  Class      Samples
  -------- ---------
  Easy           403
  Medium           8
  Hard             3

The high test accuracy must be interpreted cautiously. The small number
of Medium and Hard samples limits the strength of conclusions about
minority-class performance.

Balanced accuracy and macro F1 provide additional information, but they
do not eliminate the limitations of the small, imbalanced dataset.

These results are preliminary. Further validation, additional samples,
and stronger minority-class evaluation are needed before making claims
about generalization.

## 7. Windows Setup

### Prerequisites

-   Python 3.11
-   MSYS2 UCRT64
-   Icarus Verilog
-   VVP runtime
-   Git for version control

The Icarus Verilog installation must provide both `iverilog.exe` and
`vvp.exe`.

### Configure MSYS2

Open CMD in the directory where you cloned the repository, then change
into the project root. For example, if the repository is on your
Desktop:

``` cmd
cd /d %USERPROFILE%\Desktop\VISTA
```

Set the MSYS2 UCRT64 directory for the current CMD session:

``` cmd
set MSYS2_UCRT64_BIN=C:\msys64\ucrt64\bin
```

The simulation and integration scripts use this environment variable,
with a default fallback to the standard MSYS2 installation directory.

If MSYS2 is installed elsewhere, set `MSYS2_UCRT64_BIN` to the correct
directory.

### Activate the existing environment

``` cmd
.venv\Scripts\activate
```

### Create a new environment

If the existing environment is unavailable, create a fresh Python
environment:

``` cmd
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The requirements were installed and validated in a fresh GitHub clone
using Python 3.11 on Windows. All nine Member 2 integration tests
passed. The C17 fault simulator completed all 22 fault simulations
successfully and reported 100% fault coverage. The Streamlit dashboard
launched and displayed the C17, C432, and C499 results, ML metrics,
pattern-compaction results, and undetected-fault information. The
standard C499 integration workflow also passed its coverage-preservation
checks. The optional independent reference-verification path was not run
during this validation.

## 8. Running the C17 Fault Simulator

Run the following commands from the project root.

### Check Python syntax

``` cmd
.venv\Scripts\python.exe -m py_compile member2\simulation\c17_fault_simulator.py
```

### Run fault simulation

``` cmd
.venv\Scripts\python.exe member2\simulation\c17_fault_simulator.py member2\data\c17_faults.json member2\data\c17_rtl_analysis.json
```

The simulator uses the fault list and RTL analysis file to generate
patterns, run the golden simulation, simulate individual faults, compare
outputs, and save results.

Output:

``` text
member2/data/c17_simulation_results.json
```

The verified C17 run processed 22 faults, completed all 22 simulations
successfully, and reported 100% fault coverage.

## 9. Running the C499 Integration Workflow

The C499 integration connects Member 1's ATPG and detection-matrix
output to Member 2's test-pattern compaction process.

The current scripts expect a sibling directory named `VISTA_member1`
containing the relevant Member 1 repository and generated C499 files.

The standard C499 integration workflow was executed successfully in the
fresh clone with the expected sibling checkout available. It reduced 138
patterns to 75, retained all 750 originally detectable faults, and
reported 98.94% total fault coverage. Independent reference verification
remains a separate optional step and was not run during this validation.

### Run the standard workflow

``` cmd
.venv\Scripts\python.exe member2\optimization\run_c499_integration.py
```

The workflow:

1.  Adapts the original detection matrix.
2.  Compacts the original 138-pattern set.
3.  Verifies preservation of all 750 originally detectable faults.
4.  Creates a reduced ATPG report containing 75 patterns.
5.  Generates a fresh detection matrix.
6.  Checks the resulting fault coverage.

Expected results from the verified standard workflow:

``` text
Original patterns: 138
Selected patterns: 75
Detectable faults: 750
Verified covered faults: 750
Pattern reduction: 45.65%
Coverage preserved: True
Uncovered faults: 0
```

### Optional reference verification

``` cmd
.venv\Scripts\python.exe member2\optimization\run_c499_integration.py --verify
```

This option enables the slower independent reference-verification path
and can take considerably longer than the standard workflow.

The latest standard workflow does not run independent reference
verification; its output explicitly reports that verification was
skipped.

## 10. Running Tests

From the original VISTA project root:

``` cmd
.venv\Scripts\python.exe -m pytest
```

The current Member 2 test suite contains nine C499 integration tests.

The suite was also executed successfully in a separate environment:

``` cmd
.venv_test\Scripts\python.exe -m pytest
```

Recorded result:

``` text
9 passed
```

The separate Member 1 repository has its own test suite. A previous full
run in that repository passed 297 tests. The nine Member 2 tests do not
automatically execute the Member 1 test suite.

## 11. Dashboard

The Streamlit dashboard presents benchmark coverage, pattern-compaction
results, ML metrics, and undetected-fault information.

Dashboard file:

``` text
member2/dashboard.py
```

To start it from the project root:

``` cmd
.venv\Scripts\python.exe -m streamlit run member2/dashboard.py
```

The dashboard launched successfully in a fresh clone and displayed the
stored benchmark summaries, pattern-compaction results, ML metrics, and
undetected-fault information. However, the C499 reference-matrix lookup
still checks the sibling `VISTA_member1` directory. The dashboard has
fallback behavior, but its C499 display should be validated without that
directory before claiming that the dashboard is fully self-contained.

The dashboard's ML metrics should be interpreted with the dataset
imbalance and evaluation limitations described above.

## 12. Limitations and Future Work

### Reproducibility

-   Complete and validate a dependency manifest for all project
    components.
-   Verify the optional independent C499 reference-verification path
    from a clean checkout.
-   Remove or clearly configure the dashboard's dependency on the
    sibling `VISTA_member1` directory.
-   Reduce dependence on files in a sibling repository.
-   Document the complete integration setup and required benchmark
    files.

### Fault simulation and verification

-   Expand testing of malformed RTL and simulation failures.
-   Improve independent verification of adapter mappings and compaction
    results.
-   Add more benchmark circuits and fault models.
-   Investigate faults that remain undetected by the current pattern
    sets.

### Machine learning

-   Evaluate models using stratified or repeated validation where
    appropriate.
-   Gather stronger evidence for minority-class predictions.
-   Compare models using macro F1, balanced accuracy, per-class
    precision, and recall.
-   Avoid presenting results from small or imbalanced datasets as proof
    of generalization.

### Dashboard and experiments

-   Improve experiment reporting and dashboard integration.
-   Present total fault coverage and detectable-fault coverage
    separately.
-   Record benchmark configurations, pattern counts, fault-model
    assumptions, and verification status.
-   Make experiments reproducible from documented commands.

## 13. Research and Reporting Guidelines

-   Distinguish total fault coverage from coverage of originally
    detectable faults.
-   Separate standard simulation results from independent
    reference-verification results.
-   Clearly label preliminary ML experiments and disclose class
    imbalance.
-   Report pattern-count reduction without assuming equivalent physical
    test-time or silicon-area reduction.
-   Do not claim measured silicon performance or physical-design PPA
    improvements unless those quantities have actually been evaluated.

VISTA is a software-based VLSI testing and analysis platform. Its
current simulation and structural-analysis results do not, by
themselves, demonstrate silicon measurements or physical-design PPA
improvements.
## C499 Fault Analysis and Pattern Compaction

VISTA includes a reproducible C499 stuck-at fault-analysis workflow with pattern compaction and coverage-preservation checks.

### Verified results

- Benchmark: C499
- Fault model: Stuck-at
- Original test patterns: 138
- Compacted test patterns: 75
- Pattern-count reduction: 45.65%
- Total faults evaluated: 758
- Detected faults after compaction: 750
- Fault coverage: 98.94%
- Weighted fault coverage: 99.20%
- Originally detectable faults retained: 750/750
- Independent reference check: AGREES

Eight faults remain undetected, consistent with the original reference matrix.

### Reproduce the workflow on Windows

Install Python 3.11 and the dependencies listed in `requirements.txt`, then run:

```cmd
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pytest -v
.venv\Scripts\python.exe member2\optimization\run_c499_integration.py --verify
```

The integration requires the repository's C499 benchmark, reference input files, and VISTA engine package.

### Validation performed

The workflow was run successfully from a fresh Git clone. All nine automated tests passed, the independent reference check agreed, and the generated matrix retained all 750 originally detectable faults.

These results validate the C499 stuck-at workflow; they do not establish that every VISTA feature or benchmark has been independently validated.

## C499 Dataset Provenance

VISTA currently contains two distinct C499 experiment datasets. Their metrics must not be combined or presented as if they came from the same run.

### Reference detection-matrix experiment

- Source: `member2/data/c499_detection_matrix_recheck.json`
- Original patterns: 138
- Reduced patterns: 75
- Fault universe: 758 stuck-at faults
- Detected faults: 750/758 (98.94%)
- Undetected faults: 8
- Verification: the regenerated reduced matrix agreed with the reference check and retained all 750 originally detectable faults.
- Compaction reduction: 45.65%.

### Legacy simulation-record experiment

- Source: `member2/data/c499_simulation_results.json` and `member2/data/c499_pattern_compaction.json`
- Simulation records: 430
- Detected records: 429; undetected records: 1
- Reported coverage: 99.77%
- Pattern compaction: 1,024 to 33 (96.78% reduction), preserving all 429 detectable records in that dataset.

These datasets have different fault counts and pattern sets. Treat them as separate experiments unless their generation and fault-mapping provenance is independently established. The dashboard's C499 overview uses the 758-fault reference matrix; the master-results JSON currently includes the legacy 430-record results.
