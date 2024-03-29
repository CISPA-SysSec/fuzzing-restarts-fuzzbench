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
"""Integration code for clang source-based coverage builds."""

import os

from fuzzers import utils


def build():
    """Build benchmark."""
    cflags = [
        '-fprofile-instr-generate', '-fcoverage-mapping', '-gline-tables-only'
    ]
    #LALALA
    ldflags = []
    need_llvm_profile_continuous_mode = utils.get_need_continuous_mode(os.environ["OUT"])
    if need_llvm_profile_continuous_mode:
        cflags += ["-mllvm", "-runtime-counter-relocation"]
        ldflags += ['-fprofile-instr-generate', '-fcoverage-mapping', "-mllvm", "-runtime-counter-relocation"]
    if len(ldflags) > 0:
        utils.append_flags('LDFLAGS', ldflags)

    utils.append_flags('CFLAGS', cflags)
    utils.append_flags('CXXFLAGS', cflags)

    os.environ['CC'] = 'clang'
    os.environ['CXX'] = 'clang++'
    os.environ['FUZZER_LIB'] = '/usr/lib/libFuzzer.a'

    utils.build_benchmark()
