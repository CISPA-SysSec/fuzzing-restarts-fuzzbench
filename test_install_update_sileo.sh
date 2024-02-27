#!/bin/bash

set -e

source .venv/bin/activate

export FUZZER_NAME=sileo_aflpp_corpus_del_purge
export BENCHMARK_NAME=libpng_libpng_read_fuzzer
make build-$FUZZER_NAME-$BENCHMARK_NAME

echo "+++ Was able to successfully built fuzzer +++"

git clone https://github.com/CISPA-SysSec/fuzzing-restarts
cp -r fuzzing-restarts/sileo fuzzers/sileo_aflpp/

echo "Updated Sileo"

CWD=$(pwd)
echo "Setting result path in experiment-config-tosem.yaml to $CWD/results"

cp experiment-config-tosem.yaml experiment-config-tosem.yaml.bak
cp experiment-config-tosem-7d.yaml experiment-config-tosem-7d.yaml.bak
sed -i "s|%PATH%|$CWD|g" experiment-config-tosem.yaml
sed -i "s|%PATH%|$CWD|g" experiment-config-tosem-7d.yaml

echo "Done, please check experiment-config-tosem.yaml and experiment-config-tosem-7d.yaml"