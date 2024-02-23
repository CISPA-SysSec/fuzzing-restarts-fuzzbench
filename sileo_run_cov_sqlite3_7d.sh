#!/bin/bash

FUZZER_CONFIG="aflplusplus sileo_aflpp_corpus_del_purge sileo_aflpp_adaptive_purge"

##################

BENCHMARKS="sqlite3_ossfuzz"
BENCH_NAME="sileo-sqlite3-7d"
##################

RUNTIME="7d"
SILEO_CONFIG="$RUNTIME-$BENCH_NAME"
EXPERIMENT_NAME="$SILEO_CONFIG"


echo "$EXPERIMENT_NAME"



echo "Starting experiment"

source .venv/bin/activate

PYTHONPATH=. python3 experiment/run_experiment.py \
--experiment-config experiment-config-tosem-7d.yaml \
--benchmarks $BENCHMARKS \
--experiment-name $EXPERIMENT_NAME \
--fuzzers $FUZZER_CONFIG \
-a \
--concurrent-builds 2 

#--runners-cpus 30 \
# --measurers-cpus 10 \
