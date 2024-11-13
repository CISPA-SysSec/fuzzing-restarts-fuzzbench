#!/bin/bash

# sqlite
python3 gen_lcov.py lcov -j 80 --coverage-binary fuzzbench_data/coverage-binaries/sqlite/ossfuzz --profdata-binary llvm-profdata-14 --llvm-cov-binary llvm-cov-14 fuzzbench_data/experiment-folders/sqlite3_ossfuzz-aflplusplus_sileo_sampling/ fuzzbench_data/experiment-folders/sqlite3_ossfuzz-sileo_aflpp_corpus_del_purge_sampling/ fuzzbench_data/experiment-folders/sqlite3_ossfuzz-sileo_aflpp_rnd_purge_sampling/