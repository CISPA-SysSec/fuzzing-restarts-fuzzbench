# Fuzzing Restarts -- Experiment 5 Scripts

## Requirements

- llvm-14 (llvm-profdata-14, llvm-cov-14)
- Sileo FuzzBench sampling data (FuzzBench corpora -- corpus-XXXX.tar.gz files) for each of the fuzzers (e.g., `fuzzbench_data/experiment-folders/sqlite3_ossfuzz-aflplusplus_sileo_sampling/`)
- Coverage binaries from FuzzBench (e.g., `fuzzbench_data/coverage-binaries/sqlite/ossfuzz`)

## Disclaimer: Runtime

Note that the evaluation script has not been optimized for performance. The sampling experiments produce a large amount of data, for which coverage must be calculated via LLVM. To calculate this data and produce the heatmaps for our sampling experiments, we ran these scripts on servers with 192 physical cores (+ hyperthreads) for several days. Additionally, the sampling data itself requires approximately 200GB of disk space.

## Disclaimer: Plot Representation

The heatmaps rely on a space-filling curve for mapping the coverage vector to a 2D representation. The precise placement of individual data points may vary without **any** influence of the described effect

## How-To

Refer to the different bash scripts to understand how to run each sub-experiment. The final data will be written to `.txt` files. **The order of script execution is important!**

1. The *lcov* scripts must be executed to generate the coverage data.
2. The *median* script must be executed to find the median trial from the coverage data.
3. The heatmap and frequency scripts can then be executed.

**NOTE**: The paths in these scripts are examples and must be adjusted. After running the *median* script, you will need to update paths to reflect the correct median trials. Additionally, the scripts require significant runtime, and there will be **no** output printed while processing.
