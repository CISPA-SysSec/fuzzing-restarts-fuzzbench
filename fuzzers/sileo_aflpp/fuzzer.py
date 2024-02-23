# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Integration code for AFLplusplus fuzzer."""

import os
import re
import shutil

from fuzzers.afl import fuzzer as afl_fuzzer
from fuzzers import utils
from .sileo import sileo_main


def get_cmplog_build_directory(target_directory):
    """Return path to CmpLog target directory."""
    return os.path.join(target_directory, 'cmplog')


def get_uninstrumented_build_directory(target_directory):
    """Return path to CmpLog target directory."""
    return os.path.join(target_directory, 'uninstrumented')


def build_inner(*args):  # pylint: disable=too-many-branches,too-many-statements
    # BUILD_MODES is not already supported by fuzzbench, meanwhile we provide
    # a default configuration.

    # Add required libs for libpcap_fuzz_both.
    os.environ['EXTRA_LIBS'] = ('/usr/lib/x86_64-linux-gnu/libdbus-1.a '
                                '/lib/x86_64-linux-gnu/libsystemd.so.0')

    build_modes = list(args)
    if 'BUILD_MODES' in os.environ:
        build_modes = os.environ['BUILD_MODES'].split(',')

    # Placeholder comment.
    build_directory = os.environ['OUT']

    # If nothing was set this is the default:
    if not build_modes:
        build_modes = ['tracepc', 'cmplog', 'dict2file']

    # For bug type benchmarks we have to instrument via native clang pcguard :(
    build_flags = os.environ['CFLAGS']

    if build_flags.find(
            'array-bounds'
    ) != -1 and 'qemu' not in build_modes and 'classic' not in build_modes:
        if 'gcc' not in build_modes:
            build_modes[0] = 'native'

    # Instrumentation coverage modes:
    if 'lto' in build_modes:
        os.environ['CC'] = '/afl/afl-clang-lto'
        os.environ['CXX'] = '/afl/afl-clang-lto++'
        edge_file = build_directory + '/aflpp_edges.txt'
        os.environ['AFL_LLVM_DOCUMENT_IDS'] = edge_file
        if os.path.isfile('/usr/local/bin/llvm-ranlib-13'):
            os.environ['RANLIB'] = 'llvm-ranlib-13'
            os.environ['AR'] = 'llvm-ar-13'
            os.environ['AS'] = 'llvm-as-13'
        elif os.path.isfile('/usr/local/bin/llvm-ranlib-12'):
            os.environ['RANLIB'] = 'llvm-ranlib-12'
            os.environ['AR'] = 'llvm-ar-12'
            os.environ['AS'] = 'llvm-as-12'
        else:
            os.environ['RANLIB'] = 'llvm-ranlib'
            os.environ['AR'] = 'llvm-ar'
            os.environ['AS'] = 'llvm-as'
    elif 'qemu' in build_modes:
        os.environ['CC'] = 'clang'
        os.environ['CXX'] = 'clang++'
    elif 'gcc' in build_modes:
        os.environ['CC'] = 'afl-gcc-fast'
        os.environ['CXX'] = 'afl-g++-fast'
        if build_flags.find('array-bounds') != -1:
            os.environ['CFLAGS'] = '-fsanitize=address -O1'
            os.environ['CXXFLAGS'] = '-fsanitize=address -O1'
        else:
            os.environ['CFLAGS'] = ''
            os.environ['CXXFLAGS'] = ''
            os.environ['CPPFLAGS'] = ''
    else:
        os.environ['CC'] = '/afl/afl-clang-fast'
        os.environ['CXX'] = '/afl/afl-clang-fast++'

    print('AFL++ build: ')
    print(build_modes)

    if 'qemu' in build_modes or 'symcc' in build_modes:
        os.environ['CFLAGS'] = ' '.join(utils.NO_SANITIZER_COMPAT_CFLAGS)
        cxxflags = [utils.LIBCPLUSPLUS_FLAG] + utils.NO_SANITIZER_COMPAT_CFLAGS
        os.environ['CXXFLAGS'] = ' '.join(cxxflags)

    if 'tracepc' in build_modes or 'pcguard' in build_modes:
        os.environ['AFL_LLVM_USE_TRACE_PC'] = '1'
    elif 'classic' in build_modes:
        os.environ['AFL_LLVM_INSTRUMENT'] = 'CLASSIC'
    elif 'native' in build_modes:
        os.environ['AFL_LLVM_INSTRUMENT'] = 'LLVMNATIVE'

    # Instrumentation coverage options:
    # Do not use a fixed map location (LTO only)
    if 'dynamic' in build_modes:
        os.environ['AFL_LLVM_MAP_DYNAMIC'] = '1'
    # Use a fixed map location (LTO only)
    if 'fixed' in build_modes:
        os.environ['AFL_LLVM_MAP_ADDR'] = '0x10000'
    # Generate an extra dictionary.
    if 'dict2file' in build_modes or 'native' in build_modes:
        os.environ['AFL_LLVM_DICT2FILE'] = build_directory + '/afl++.dict'
    # Enable context sentitivity for LLVM mode (non LTO only)
    if 'ctx' in build_modes:
        os.environ['AFL_LLVM_CTX'] = '1'
    # Enable N-gram coverage for LLVM mode (non LTO only)
    if 'ngram2' in build_modes:
        os.environ['AFL_LLVM_NGRAM_SIZE'] = '2'
    elif 'ngram3' in build_modes:
        os.environ['AFL_LLVM_NGRAM_SIZE'] = '3'
    elif 'ngram4' in build_modes:
        os.environ['AFL_LLVM_NGRAM_SIZE'] = '4'
    elif 'ngram5' in build_modes:
        os.environ['AFL_LLVM_NGRAM_SIZE'] = '5'
    elif 'ngram6' in build_modes:
        os.environ['AFL_LLVM_NGRAM_SIZE'] = '6'
    elif 'ngram7' in build_modes:
        os.environ['AFL_LLVM_NGRAM_SIZE'] = '7'
    elif 'ngram8' in build_modes:
        os.environ['AFL_LLVM_NGRAM_SIZE'] = '8'
    elif 'ngram16' in build_modes:
        os.environ['AFL_LLVM_NGRAM_SIZE'] = '16'
    if 'ctx1' in build_modes:
        os.environ['AFL_LLVM_CTX_K'] = '1'
    elif 'ctx2' in build_modes:
        os.environ['AFL_LLVM_CTX_K'] = '2'
    elif 'ctx3' in build_modes:
        os.environ['AFL_LLVM_CTX_K'] = '3'
    elif 'ctx4' in build_modes:
        os.environ['AFL_LLVM_CTX_K'] = '4'

    # Only one of the following OR cmplog
    # enable laf-intel compare splitting
    if 'laf' in build_modes:
        os.environ['AFL_LLVM_LAF_SPLIT_SWITCHES'] = '1'
        os.environ['AFL_LLVM_LAF_SPLIT_COMPARES'] = '1'
        os.environ['AFL_LLVM_LAF_SPLIT_FLOATS'] = '1'
        if 'autodict' not in build_modes:
            os.environ['AFL_LLVM_LAF_TRANSFORM_COMPARES'] = '1'

    if 'eclipser' in build_modes:
        os.environ['FUZZER_LIB'] = '/libStandaloneFuzzTarget.a'
    else:
        os.environ['FUZZER_LIB'] = '/libAFLDriver.a'

    # Some benchmarks like lcms
    # (see: https://github.com/mm2/Little-CMS/commit/ab1093539b4287c233aca6a3cf53b234faceb792#diff-f0e6d05e72548974e852e8e55dffc4ccR212)
    # fail to compile if the compiler outputs things to stderr in unexpected
    # cases. Prevent these failures by using AFL_QUIET to stop afl-clang-fast
    # from writing AFL specific messages to stderr.
    os.environ['AFL_QUIET'] = '1'
    os.environ['AFL_MAP_SIZE'] = '2621440'

    src = os.getenv('SRC')
    work = os.getenv('WORK')

    with utils.restore_directory(src), utils.restore_directory(work):
        # Restore SRC to its initial state so we can build again without any
        # trouble. For some OSS-Fuzz projects, build_benchmark cannot be run
        # twice in the same directory without this.
        utils.build_benchmark()

    if 'cmplog' in build_modes and 'qemu' not in build_modes:

        # CmpLog requires an build with different instrumentation.
        new_env = os.environ.copy()
        new_env['AFL_LLVM_CMPLOG'] = '1'

        # For CmpLog build, set the OUT and FUZZ_TARGET environment
        # variable to point to the new CmpLog build directory.
        cmplog_build_directory = get_cmplog_build_directory(build_directory)
        os.mkdir(cmplog_build_directory)
        new_env['OUT'] = cmplog_build_directory
        fuzz_target = os.getenv('FUZZ_TARGET')
        if fuzz_target:
            new_env['FUZZ_TARGET'] = os.path.join(cmplog_build_directory,
                                                  os.path.basename(fuzz_target))

        print('Re-building benchmark for CmpLog fuzzing target')
        utils.build_benchmark(env=new_env)

    if 'symcc' in build_modes:

        symcc_build_directory = get_uninstrumented_build_directory(
            build_directory)
        os.mkdir(symcc_build_directory)

        # symcc requires an build with different instrumentation.
        new_env = os.environ.copy()
        new_env['CC'] = '/symcc/build/symcc'
        new_env['CXX'] = '/symcc/build/sym++'
        new_env['SYMCC_OUTPUT_DIR'] = '/tmp'
        new_env['CXXFLAGS'] = new_env['CXXFLAGS'].replace("-stlib=libc++", "")
        new_env['FUZZER_LIB'] = '/libfuzzer-harness.o'
        new_env['OUT'] = symcc_build_directory
        new_env['SYMCC_LIBCXX_PATH'] = "/libcxx_native_build"
        new_env['SYMCC_NO_SYMBOLIC_INPUT'] = "1"
        new_env['SYMCC_SILENT'] = "1"

        # For symcc build, set the OUT and FUZZ_TARGET environment
        # variable to point to the new symcc build directory.
        new_env['OUT'] = symcc_build_directory
        fuzz_target = os.getenv('FUZZ_TARGET')
        if fuzz_target:
            new_env['FUZZ_TARGET'] = os.path.join(symcc_build_directory,
                                                  os.path.basename(fuzz_target))

        print('Re-building benchmark for symcc fuzzing target')
        utils.build_benchmark(env=new_env)

    shutil.copy('/afl/afl-fuzz', build_directory)
    if os.path.exists('/afl/afl-qemu-trace'):
        shutil.copy('/afl/afl-qemu-trace', build_directory)
    if os.path.exists('/aflpp_qemu_driver_hook.so'):
        shutil.copy('/aflpp_qemu_driver_hook.so', build_directory)
    if os.path.exists('/get_frida_entry.sh'):
        shutil.copy('/afl/afl-frida-trace.so', build_directory)
        shutil.copy('/get_frida_entry.sh', build_directory)
    
    
    # for sileo corpus minimization (afl-cmin, afl-tmin, afl-showmap are needed)
    if os.path.exists('/afl/afl-cmin'):
        shutil.copy('/afl/afl-cmin', build_directory)
    if os.path.exists('/afl/afl-tmin'):
        shutil.copy('/afl/afl-tmin', build_directory)
    if os.path.exists('/afl/afl-showmap'):
        shutil.copy('/afl/afl-showmap', build_directory)

def build(*args):  # pylint: disable=too-many-branches,too-many-statements
    """Build benchmark."""
    build_modes = list(args)
    # region: TO_GENERATE, build_settings
    # endregion: TO_GENERATE, build_settings
    build_inner(*build_modes)


def check_skip_det_compatible(additional_flags):
    """ Checks if additional flags are compatible with '-d' option"""
    # AFL refuses to take in '-d' with '-M' or '-S' options for parallel mode.
    # (cf. https://github.com/google/AFL/blob/8da80951/afl-fuzz.c#L7477)
    if '-M' in additional_flags or '-S' in additional_flags:
        return False
    return True


def fuzz_inner(input_corpus,
               output_corpus,
               target_binary,
               add_flags=tuple(),
               skip=False,
               no_cmplog=False,
               sileo_mode="random",
               sileo_purge="permit_purge",
               sileo_instances_num=1,
               sileo_rtime="",
               sileo_log_level="DEBUG",
               sileo_cmin = False,
               ):  # pylint: disable=too-many-arguments
    """Run fuzzer. 
    add_flags: extra flags for afl-fuzz or other base fuzzers; 
    skip: if set to False, AFL_DISABLE_TRIM=1, AFL_CMPLOG_ONLY_NEW=1, use ADDITIONAL_ARGS
    no_cmplog: if set to True, even we have cmplog binary, we do not use it.
    sileo_mode: restart mode
    sileo_purge: 1. purge: try to restart every sileo_restart_time even if we find a new path 2. no_purge: do not permit purge; 3. permit_purge: restart after 1/2 of the runtime if the strategy permits and no restarts happened yet
    sileo_restart_time: we will try to check if we can restart every sileo_restart_time. format: [0-9.][dhm]. e.g: 2d, 30min, 0.5h; if set to None, then we will use the default restart time
    sileo_cmin: Run corpus minimization after every restart
    """

    # Calculate CmpLog binary path from the instrumented target binary.
    target_binary_directory = os.path.dirname(target_binary)
    cmplog_target_binary_directory = (
        get_cmplog_build_directory(target_binary_directory))
    target_binary_name = os.path.basename(target_binary)
    cmplog_target_binary = os.path.join(cmplog_target_binary_directory,
                                        target_binary_name)

    afl_fuzzer.prepare_fuzz_environment(input_corpus)
    # decomment this to enable libdislocator.
    # os.environ['AFL_ALIGNED_ALLOC'] = '1' # align malloc to max_align_t
    # os.environ['AFL_PRELOAD'] = '/afl/libdislocator.so'

    add_flags = list(add_flags)

    if os.path.exists('./afl++.dict'):
        add_flags += ['-x', './afl++.dict']

    # Move the following to skip for upcoming _double tests:
    if os.path.exists(cmplog_target_binary) and no_cmplog is False:
        add_flags += ['-c', cmplog_target_binary]
        print('CmpLog target: ' + cmplog_target_binary)

    os.environ['AFL_IGNORE_TIMEOUTS'] = '1'
    os.environ['AFL_IGNORE_UNKNOWN_ENVS'] = '1'
    os.environ['AFL_FAST_CAL'] = '1'

    if not skip:
        os.environ['AFL_DISABLE_TRIM'] = "1"
        os.environ['AFL_CMPLOG_ONLY_NEW'] = '1'
        if 'ADDITIONAL_ARGS' in os.environ:
            add_flags += os.environ['ADDITIONAL_ARGS'].split(' ')

    build_dir: str = os.environ['OUT']

    flags = []
    flags += ['--add_flags']

    if not add_flags or check_skip_det_compatible(add_flags):
        flags += ['-d']
    if add_flags:
        flags += add_flags
    dictionary_path = utils.get_dictionary_path(target_binary)
    if dictionary_path:
        flags += ['-x', dictionary_path]

    assert isinstance(sileo_mode, str) and len(sileo_mode) > 0 and len(sileo_mode) > 0
    assert isinstance(sileo_rtime, str) and (len(sileo_rtime) == 0 or re.match("[0-9.]+[hdm](-[0-9.]+[hdm])?", sileo_rtime))
    assert sileo_purge in {"purge", "no_purge", "permit_purge", "force"}
    sileo_flags = ["--log", sileo_log_level, "--mode", sileo_mode, "--num", str(sileo_instances_num)]
    if len(sileo_rtime) > 0:
        sileo_flags += ["--rtime", sileo_rtime]
    if sileo_purge == "permit_purge":
        pass
    elif sileo_purge == "purge":
        sileo_flags.append("--purge")
    elif sileo_purge == "force":
        sileo_flags.append("--purge")
        sileo_flags.append("--force_restart")
    else:
        assert sileo_purge == "no_purge"
        sileo_flags.append("--no_purge")
    if sileo_cmin:
        sileo_flags.append("--cmin")

    total_fuzzing_time_hr = int(int(os.getenv('MAX_TOTAL_TIME', "86400")) / 3600)
    sileo_flags += ["--runtime", str(total_fuzzing_time_hr)]

    sileo_main.main(sileo_flags + ["--afl_bin", build_dir + "/afl-fuzz", "-s", input_corpus, "-o", output_corpus, "-t", target_binary] + flags)


def fuzz(input_corpus,
         output_corpus,
         target_binary
         ):  # pylint: disable=too-many-arguments
    """Run fuzzer. """
    kwargs = {
        "input_corpus": input_corpus,
        "output_corpus": output_corpus,
        "target_binary": target_binary,
    }
    # region: TO_GENERATE, fuzz_settings
    kwargs["sileo_mode"] = 'none'
    kwargs["sileo_purge"] = 'no_purge'
    # endregion: TO_GENERATE, fuzz_settings
    fuzz_inner(**kwargs)