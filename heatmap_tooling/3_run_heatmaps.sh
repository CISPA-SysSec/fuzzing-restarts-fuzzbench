#!/bin/bash

# libpng
python3 gen_lcov.py heatmap --output graph_out/ --baseline fuzzbench_data/experiment-folders/libpng_libpng_read_fuzzer-aflplusplus_sileo_sampling/trial-10/ fuzzbench_data/experiment-folders/libpng_libpng_read_fuzzer-sileo_aflpp_corpus_del_purge_sampling/trial-66 fuzzbench_data/experiment-folders/libpng_libpng_read_fuzzer-sileo_aflpp_rnd_purge_sampling/trial-39 fuzzbench_data/experiment-folders/libpng_libpng_read_fuzzer-aflplusplus_sileo_sampling/trial-6/

# libpcap
python3 gen_lcov.py heatmap --output graph_out/ --baseline fuzzbench_data/experiment-folders/libpcap_fuzz_both-aflplusplus_sileo_sampling/trial-16/ fuzzbench_data/experiment-folders/libpcap_fuzz_both-sileo_aflpp_corpus_del_purge_sampling/trial-72/ fuzzbench_data/experiment-folders/libpcap_fuzz_both-sileo_aflpp_rnd_purge_sampling/trial-46 fuzzbench_data/experiment-folders/libpcap_fuzz_both-aflplusplus_sileo_sampling/trial-15/
#python3 gen_lcov.py heatmap --output graph_out/ --baseline fuzzbench_data/experiment-folders/libpcap_fuzz_both-aflplusplus_sileo_sampling/trial-15/ fuzzbench_data/experiment-folders/libpcap_fuzz_both-sileo_aflpp_corpus_del_purge_sampling/trial-72/ fuzzbench_data/experiment-folders/libpcap_fuzz_both-sileo_aflpp_rnd_purge_sampling/trial-46 fuzzbench_data/experiment-folders/libpcap_fuzz_both-aflplusplus_sileo_sampling/trial-14/

# sqlite
python3 gen_lcov.py heatmap --output graph_out/ --baseline fuzzbench_data/experiment-folders/sqlite3_ossfuzz-aflplusplus_sileo_sampling/trial-21 fuzzbench_data/experiment-folders/sqlite3_ossfuzz-aflplusplus_sileo_sampling/trial-30 fuzzbench_data/experiment-folders/sqlite3_ossfuzz-sileo_aflpp_corpus_del_purge_sampling/trial-82 fuzzbench_data/experiment-folders/sqlite3_ossfuzz-sileo_aflpp_rnd_purge_sampling/trial-53
#python3 gen_lcov.py heatmap --output graph_out/ --baseline fuzzbench_data/experiment-folders/sqlite3_ossfuzz-aflplusplus_sileo_sampling/trial-30/ fuzzbench_data/experiment-folders/sqlite3_ossfuzz-sileo_aflpp_corpus_del_purge_sampling/trial-82/ fuzzbench_data/experiment-folders/sqlite3_ossfuzz-sileo_aflpp_rnd_purge_sampling/trial-58 fuzzbench_data/experiment-folders/sqlite3_ossfuzz-aflplusplus_sileo_sampling/trial-29/
