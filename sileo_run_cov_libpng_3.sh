#!/bin/bash


FUZZER_CONFIG="aflplusplus sileo_aflpp_corpus_del_purge sileo_aflpp_corpus_del_force_30 sileo_aflpp_corpus_del_force_60 sileo_aflpp_corpus_del_force_240"

##################

BENCHMARKS="libpng_libpng_read_fuzzer"
BENCH_NAME="sileo-libpng-3n"
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
--concurrent-builds 2 

#--runners-cpus 30 \
# --measurers-cpus 10 \
