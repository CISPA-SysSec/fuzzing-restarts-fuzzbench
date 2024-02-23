import os
import third_party.sileo_gen as sileo_gen

def get_args_of_aflplusplus_build(fuzzer_python_fmt_fpath):
    os_env = [('PYTHONPATH', '/src'), ('benchmark', 'zlib_zlib_uncompress_fuzzer'), ('PYTHON_VERSION', '3.10.8'), ('PWD', '/src/zlib'), ('SRC', '/src'), ('HOME', '/root'), ('LIB_FUZZING_ENGINE', '/usr/lib/libFuzzingEngine.a'), ('CMAKE_VERSION', '3.24.2'), ('FUZZER', 'coverage'), ('FUZZINTRO_OUTDIR', '/src'),  ('WORK', '/work'), ('PATH', '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/out'), ('CC', 'clang'), ('DEBIAN_FRONTEND', 'noninteractive'), ('OUT', '/out'), ('_', '/usr/local/bin/python3'), ("LOCAL_EXPERIMENT", "True"), ("FUZZ_TARGET", "zlib_uncompress_fuzzer"), ("REPORT_FILESTORE", "/home/xxu/fuzzbench/tmp/sileo_gen_running_results/report-data"), ("EXPERIMENT_FILESTORE", "/home/xxu/fuzzbench/tmp/sileo_gen_running_results/experiment-data"), ("INSTANCE_NAME", "r-tmpexp0-1"), ("FUZZER", "sileo_aflpp"), ("BENCHMARK", "zlib_zlib_uncompress_fuzzer"), ("EXPERIMENT", "tmpexp0"), ("TRIAL_ID", "1"),  ("CFLAGS", "-DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION -pthread -Wl,--no-as-needed -Wl,-ldl -Wl,-lm -Wno-unused-command-line-argument -O3")]
    for (k, v) in os_env:
        os.environ[k] = v
    return sileo_gen.get_env_pseudo(fuzzer_python_fmt_fpath,
                          [("build", dict())],
                          [("afl_fuzzer.prepare_fuzz_environment", None, True, True),
                           ("utils.restore_directory", sileo_gen.DummyContextManager(
                               sileo_gen.dummy_context_func), False, True),
                           ("utils.build_benchmark", None, True, True),
                           ("os.mkdir", True, False, True)
                           ] +
                          [("shutil." + funcname, True, False, True) for funcname in [
                              "copyfileobj", "copyfile", "copymode", "copystat", "copy", "copy2", "copytree", "move", "rmtree",
                              "make_archive", "get_archive_formats", "register_archive_format", "unregister_archive_format", "get_unpack_formats",
                              "register_unpack_format", "unregister_unpack_format", "unpack_archive", "ignore_patterns", "chown", "which", "get_terminal_size"]])


if __name__ == '__main__':
    print(get_args_of_aflplusplus_build("fuzzers.aflplusplus.fuzzer"))