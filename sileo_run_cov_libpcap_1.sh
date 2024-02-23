#!/bin/bash


FUZZER_CONFIG="aflplusplus sileo_aflpp_rnd_purge sileo_aflpp_input_shuffle_purge sileo_aflpp_corpus_del_purge"

##################

BENCHMARKS="libpcap_fuzz_both"
BENCH_NAME="sileo-libpcap-1n"
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

#--runners-cpus 40 \
# --measurers-cpus 10 \
