#!/bin/bash

echo "starting libpng"
# libpng
python3 gen_lcov.py frequency --output graph_out/ fuzzbench_data/experiment-folders/libpng_libpng_read_fuzzer-sileo_aflpp_corpus_del_purge_sampling/ fuzzbench_data/experiment-folders/libpng_libpng_read_fuzzer-sileo_aflpp_rnd_purge_sampling/ fuzzbench_data/experiment-folders/libpng_libpng_read_fuzzer-aflplusplus_sileo_sampling/ &

echo "starting libpcap"
# libpcap
python3 gen_lcov.py frequency --output graph_out/ fuzzbench_data/experiment-folders/libpcap_fuzz_both-sileo_aflpp_corpus_del_purge_sampling/ fuzzbench_data/experiment-folders/libpcap_fuzz_both-sileo_aflpp_rnd_purge_sampling/ fuzzbench_data/experiment-folders/libpcap_fuzz_both-aflplusplus_sileo_sampling/ &

echo "starting sqlite"
# sqlite
python3 gen_lcov.py frequency --output graph_out/ fuzzbench_data/experiment-folders/sqlite3_ossfuzz-aflplusplus_sileo_sampling/ fuzzbench_data/experiment-folders/sqlite3_ossfuzz-sileo_aflpp_corpus_del_purge_sampling/ fuzzbench_data/experiment-folders/sqlite3_ossfuzz-sileo_aflpp_rnd_purge_sampling/ &

wait
