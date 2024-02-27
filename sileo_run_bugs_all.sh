#!/bin/bash

FUZZER_CONFIG="aflplusplus sileo_aflpp_corpus_del_purge sileo_aflpp_adaptive_purge"

##################
BENCHMARKS="aspell_aspell_fuzzer grok_grk_decompress_fuzzer file_magic_fuzzer arrow_parquet-arrow-fuzz harfbuzz_hb-shape-fuzzer_17863b bloaty_fuzz_target_52948c libxml2_xml_e85b9b mbedtls_fuzz_dtlsclient_7c6b0e"
BENCH_NAME="sileo-bugs-all"
##################

RUNTIME="24h"
SILEO_CONFIG="$RUNTIME-$BENCH_NAME"
EXPERIMENT_NAME="$SILEO_CONFIG"


echo "$EXPERIMENT_NAME"

echo "Starting experiment"

source .venv/bin/activate

PYTHONPATH=. python3 experiment/run_experiment.py \
--experiment-config experiment-config-tosem.yaml \
--benchmarks $BENCHMARKS \
--experiment-name $EXPERIMENT_NAME \
--fuzzers $FUZZER_CONFIG \
-a \
--runners-cpus 40 \
--measurers-cpus 10 \
--concurrent-builds 2
