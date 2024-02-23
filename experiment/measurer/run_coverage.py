# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module for running a clang source-based coverage instrumented binary
on a corpus."""

import os
import subprocess
import tempfile
import threading
from typing import List
import traceback #LALALA

from common import experiment_utils
from common import logs
from common import new_process
from common import sanitizer
from common import benchmark_utils #LALALA
from experiment.measurer import measurer_sileo_extra_utils #LALALA

logger = logs.Logger()

# Time buffer for libfuzzer merge to gracefully exit.
EXIT_BUFFER = 15

# Memory limit for libfuzzer merge.
RSS_LIMIT_MB = 2048

# Per-unit processing timeout for libfuzzer merge.
UNIT_TIMEOUT = 10

# Max time to spend on libfuzzer merge.
MAX_TOTAL_TIME = experiment_utils.get_snapshot_seconds()

class NewThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}):
        threading.Thread.__init__(self, group, target, name, args, kwargs)

    def run(self):
        if self._target != None:
            self.result = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        threading.Thread.join(self, *args)
        return self.result
    

def clear_failed_coverage_run(meta_dir):
    measurer_sileo_extra_utils.reset_filter4sileo_filter_inputs_redundancy4coverage(meta_dir)

def do_coverage_inner(coverage_binary, crashes_dir, new_units_dir, coverage_binary_dir, profraw_file_pattern, timeout, need_profile_output):
    with tempfile.TemporaryDirectory() as merge_dir:    
        command = [
            coverage_binary, '-merge=1', '-dump_coverage=1',
            f'-artifact_prefix={crashes_dir}/', f'-timeout={timeout}',
            f'-rss_limit_mb={RSS_LIMIT_MB}',
            f'-max_total_time={MAX_TOTAL_TIME - EXIT_BUFFER}',
            merge_dir,
            new_units_dir
        ]
        env = os.environ.copy()
        env['LLVM_PROFILE_FILE'] = profraw_file_pattern
        env['LD_LIBRARY_PATH'] = env.get("LD_LIBRARY_PATH", "") + ":" + os.path.dirname(coverage_binary)
        sanitizer.set_sanitizer_options(env)
        if need_profile_output:
            output_file = None
            err_file = None
        else:
            output_file = subprocess.DEVNULL
            err_file = subprocess.DEVNULL
        try:
            result = new_process.execute(command,
                                        env=env,
                                        cwd=coverage_binary_dir,
                                        expect_zero=False,
                                        kill_children=True,
                                        output_file=output_file,
                                        err_file=err_file
                                        )#timeout=MAX_TOTAL_TIME)
        except Exception as e:
            traceback.print_exc()
            return -1, str(e)
    return result.retcode, result.output

def do_coverage_run(  # pylint: disable=too-many-locals
        coverage_binary: str, new_units_dir: List[str],
        profraw_file_pattern: str, crashes_dir: str, cycle: int):
    """Does a coverage run of |coverage_binary| on |new_units_dir|. Writes
    the result to |profraw_file_pattern|."""
    if measurer_sileo_extra_utils.ENABLE_SILEO_FILTER:
        meta_dir = measurer_sileo_extra_utils.get_meta_sileo_filter_inputs_redundancy4coverage_dir(new_units_dir)
        new_units_dir_new = measurer_sileo_extra_utils.get_tmp_sileo_filter_inputs_redundancy4coverage_dir(new_units_dir)
        if cycle < 1:
            measurer_sileo_extra_utils.reset_filter4sileo_filter_inputs_redundancy4coverage(meta_dir)
        new_units_dir_new = measurer_sileo_extra_utils.sileo_filter_inputs_redundancy4coverage(new_units_dir, new_units_dir_new, meta_dir)
    else:
        meta_dir = ""
        new_units_dir_new = new_units_dir
    coverage_binary_dir = os.path.dirname(coverage_binary)

    timeout = benchmark_utils.get_timeout(coverage_binary_dir)
    need_profile_output = benchmark_utils.get_need_profile_output(coverage_binary_dir)
    jobs = benchmark_utils.get_job_number_of_libfuzzer(coverage_binary_dir)
    logger.info(f"Use special timeout: {timeout}")
    if timeout <= 0:
        timeout = UNIT_TIMEOUT
        jobs = 1

    if jobs > 1:
        jobs, split_dirs = measurer_sileo_extra_utils.split_corpus_dir(new_units_dir_new, jobs)
    else:    
        split_dirs = [new_units_dir_new]
    
    results = []
    if jobs > 1:
        ths = [NewThread(target=do_coverage_inner, args=[coverage_binary, crashes_dir, split_dir, coverage_binary_dir, profraw_file_pattern, timeout, need_profile_output]) for split_dir in split_dirs]
        for th in ths:
            th.start()
        for th in ths:
            th.join()
            results.append(th.result)
    else:
        results.append(do_coverage_inner(coverage_binary, crashes_dir, new_units_dir_new, coverage_binary_dir, profraw_file_pattern, timeout, need_profile_output))
    
    for (retcode, output) in results:
        if retcode != 0:
            if output is None:
                output = ""
            logger.error('Coverage run failed.',
                        extras={
                            'coverage_binary': coverage_binary,
                            'output': output[-new_process.LOG_LIMIT_FIELD:],
                        })
            clear_failed_coverage_run(meta_dir)
