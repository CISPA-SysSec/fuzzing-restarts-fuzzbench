# Fuzzing Restarts: FuzzBench

This repository is part of our paper *[Novelty Not Found: Adaptive Fuzzer Restarts to Improve Input Space Coverage](https://mschloegel.me/paper/schiller2023fuzzerrestarts.pdf)*. This repository contains a patched version of FuzzBench, which features custom settings to reduce the disk space overhead by storing just to last two corpus archives and some minor bug fixes.

**Options (for experiment config yaml files):**

- **sileo_allow_overwrite_existing_experiment:** `true `/ `false`
- **sileo_only_keep_last_corpus:** `true `/ `false`

## Setup

The following describes how to setup FuzzBench. Make sure you also have installed Docker and your user is part of the *docker* group.

1. Clone this repository:

   ``` bash
    git clone https://github.com/CISPA-SysSec/fuzzing-restarts-fuzzbench.git && cd fuzzing-restarts-fuzzbench
   ```

2. Install required packages (**Note: Python in version 3.10 is required**):
   With **apt** / **apt-get** (Ubuntu / Debian based)

   ``` bash
    sudo apt-get install build-essential rsync python3.10-dev python3.10-venv
   ```

3. Install requirements and build dependencies:

    ```bash
     make install-dependencies
    ```

4. Test installation:

   ```bash
    ./test_install_update_sileo.sh
   ```

## Reproduce Paper Results

If you want to reproduce our experiments from our paper, you can use our `sileo_run_*` scripts. These scripts using the experiment configuration files `experiment-config.yaml` and `experiment-config-7d.yaml`. In these files the runtime and also the number of trials are specified. If you have not enough computation power, you can reduce the number of trials to e.g. 5, but we highly recommend to use 10 trial or even more to get statistically significant results. There are different types of experiments that can be executed using this scripts. The script names indicate the respective experiments. Execute such a script in a `tmux` session.

  ```bash
    tmux new -s fuzzing-restarts
    ./sileo_run_cov_all.sh
  ```

**Important**: Please make sure to change / add the following into the run scripts, to ensure a proper utilization of your hardware. You can have a look at `sileo_run_bugs_1.sh` where we used 40 runner CPUs and 10 measurer CPUs, on our hardware with 52 pysical cores and 52 hyperthreads (We ignored the hyperthreads and just executed as much parallel jobs as we have physical cores). If you dont set this, all jobs at once will be executed and no core pinning happens!

```bash
--runners-cpus NUMBER_RUNNER_CPUS \
--measurers-cpus NUMBER_MEASURER_CPUS \
```

If you have assigned enough `runners-cpus` (number_of_fuzzers \* number_of_target \* number_of_trials == number_of_jobs) e.g. for `sileo_run_cov_bloaty_1.sh`: 4 fuzzers \* 1 target \* 10 trials == 40 jobs. If you assign **40** runners-cpus, the fuzzing campaing will take 24 hours and the overall runtime (including the coverage measurement) will take maybe somewhat longer, depending on the number of `measurement-cpus` you set. If you assign less `runner-cpus` than overall jobs, e.g. `--runners-cpus 20` fuzzbench will schedule the jobs and the overall runtime will be in this case 48 hours.

---

### Notes

The names of our Sileo strategies differ in our code compared to the paper, each strategy refers to a own fuzzer in FuzzBench and can be found in `fuzzers/sileo_aflpp_*`. In the following, you can find the mapping between the name from our code and the name in the paper:

- *corpus_del*: Sileo Corus Pruning
- *input_shuffle*: Sileo Input Shuffle
- *rnd*: Sileo Reset
- *tree_chopper*: Sileo Tree Chopper
- *tree_planter*: Sileo Tree Planter
- *timeback_plain*: Sileo Timeback
- *adaptive*: Sileo Ensemble
- *continue*: Not named in the paper, but refers to *input_shuffle* without copying all inputs (See Discussion Section). We recommend this instead of input_shuffle to reduce disk usage.

The fuzzer names also show its restart heuristic:

- *\*_purge*: threshold-based restarts
- *\*_force_MINUTES*: force restart after restart time in MINUTES
- *\*_sampling*: the fuzzer / strategy is configured using our patched aflplusplus (for sampling experiments)
- *\*_cmin*: the fuzzer / strategy uses *afl-cmin* (using AFL++ 4.06)

---

For the coverage experiments, there exist three different `sileo_run_*` scripts per target, which are use different types of Sileo strategies:

- `*_1.sh`
  - this is the fuzzer configuration from the paper
    - AFL++ (competitor)
    - Sileo Corpus Pruning (best performing overall)
    - Sileo Reset (baseline for a full corpus reset)
    - Sileo Input Shuffle (baseline for no corpus retention) (We recommend to replace it with *sileo_aflpp_continue_purge*)
  - **Fuzzers**: aflplusplus, sileo_aflpp_corp_del_purge, sileo_aflpp_input_shuffle_purge, sileo_aflpp_random_purge
- `*_2.sh`
  - this is the fuzzer configuration for our other strategies + AFL++ as competitor
  - **Fuzzers**: aflplusplus, sileo_aflpp_tree_chopper_multi_purge, sileo_aflpp_tree_planter_purge, sileo_aflpp_timeback_plain_purge
- `*_3.sh`:
  - this is the fuzzer configuration for Sileo with fixed restart times + AFL++ as competitor
  - **Fuzzers**: aflplusplus, sileo_aflpp_corp_del_purge, sileo_aflpp_corpus_del_force_30, sileo_aflpp_corpus_del_force_60, sileo_aflpp_corpus_del_force_240
- `*_cov_all.sh`:
  - this uses also the fuzzer configuration from the paper, but all targets at once for the coverage experiment.
- `*_bugs_all.sh`:
  - this uses also the fuzzer configuration from the paper, but all targets at once for the bug experiment.

As an example:

- `sileo_run_cov_libpcap_1.sh`  --- run our default coverage experiment from the paper on the target *libpcap*
- `sileo_run_cov_libpng_3.sh`  --- run the coverage experiment with fixed restart times from the paper on the target *libpng*

The experiment results and reports are stored in [results](results).

---

## FuzzBench: Fuzzer Benchmarking As a Service

FuzzBench is a free service that evaluates fuzzers on a wide variety of
real-world benchmarks, at Google scale. The goal of FuzzBench is to make it
painless to rigorously evaluate fuzzing research and make fuzzing research
easier for the community to adopt. We invite members of the research community
to contribute their fuzzers and give us feedback on improving our evaluation
techniques.

FuzzBench provides:

* An easy API for integrating fuzzers.
* Benchmarks from real-world projects. FuzzBench can use any
  [OSS-Fuzz](https://github.com/google/oss-fuzz) project as a benchmark.
* A reporting library that produces reports with graphs and statistical tests
  to help you understand the significance of results.

To participate, submit your fuzzer to run on the FuzzBench platform by following
[our simple guide](
https://google.github.io/fuzzbench/getting-started/).
After your integration is accepted, we will run a large-scale experiment using
your fuzzer and generate a report comparing your fuzzer to others.
See [a sample report](https://www.fuzzbench.com/reports/sample/index.html).

### Overview
<kbd>
  
![FuzzBench Service diagram](docs/images/FuzzBench-service.png)
  
</kbd>


### Sample Report

You can view our sample report
[here](https://www.fuzzbench.com/reports/sample/index.html) and
our periodically generated reports
[here](https://www.fuzzbench.com/reports/index.html).
The sample report is generated using 10 fuzzers against 24 real-world
benchmarks, with 20 trials each and over a duration of 24 hours.
The raw data in compressed CSV format can be found at the end of the report.

When analyzing reports, we recommend:
* Checking the strengths and weaknesses of a fuzzer against various benchmarks.
* Looking at aggregate results to understand the overall significance of the
  result.

Please provide feedback on any inaccuracies and potential improvements (such as
integration changes, new benchmarks, etc.) by opening a GitHub issue
[here](https://github.com/google/fuzzbench/issues/new).

### Documentation

Read our [detailed documentation](https://google.github.io/fuzzbench/) to learn
how to use FuzzBench.

### Contacts

Join our [mailing list](https://groups.google.com/forum/#!forum/fuzzbench-users)
for discussions and announcements, or send us a private email at
[fuzzbench@google.com](mailto:fuzzbench@google.com).
