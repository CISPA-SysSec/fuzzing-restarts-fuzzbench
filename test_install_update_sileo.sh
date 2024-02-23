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