#!/bin/bash

# libpcap
python3 gen_lcov.py lcov -j 80 --coverage-binary fuzzbench_data/coverage-binaries/libpcap/fuzz_both --profdata-binary llvm-profdata-14 --llvm-cov-binary llvm-cov-14 fuzzbench_data/experiment-folders/libpcap_fuzz_both-aflplusplus_sileo_sampling/ fuzzbench_data/experiment-folders/libpcap_fuzz_both-sileo_aflpp_corpus_del_purge_sampling/ fuzzbench_data/experiment-folders/libpcap_fuzz_both-sileo_aflpp_rnd_purge_sampling/
