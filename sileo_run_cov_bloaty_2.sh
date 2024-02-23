#!/bin/bash

FUZZER_CONFIG="aflplusplus sileo_aflpp_tree_chopper_multi_purge sileo_aflpp_tree_planter_purge sileo_aflpp_timeback_plain_purge"

##################

BENCHMARKS="bloaty_fuzz_target"
BENCH_NAME="sileo-bloaty-2n"
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
