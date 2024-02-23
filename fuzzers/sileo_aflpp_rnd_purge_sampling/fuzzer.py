from fuzzers.sileo_aflpp import fuzzer as main_sileo_fuzzer
import os


def build(*args) -> None:
    build_modes = list(args)
    # region: TO_GENERATE, build_settings
    build_modes = ['tracepc', 'cmplog', 'dict2file']
    # endregion: TO_GENERATE, build_settings
    main_sileo_fuzzer.build_inner(*build_modes)


# pylint: disable=too-many-arguments
def fuzz(input_corpus,
         output_corpus,
         target_binary):
    """Run fuzzer. """
    kwargs = {
        "input_corpus": input_corpus,
        "output_corpus": output_corpus,
        "target_binary": target_binary,
    }
    # region: TO_GENERATE, fuzz_settings
    kwargs["sileo_mode"] = 'random'
    kwargs["sileo_purge"] = 'purge'
    kwargs["sileo_rtime"] = '5m-30m'
    
    os.environ["SILEO_SAMPLING_RATE"] = '10000'
    os.environ["SILEO_SAMPLING_DIR"] = os.path.join(output_corpus if os.environ["LOCAL_EXPERIMENT"].lower().strip() == "false" else os.path.join(os.environ["EXPERIMENT_FILESTORE"], os.environ["EXPERIMENT"], "experiment-folders", os.environ["BENCHMARK"] + "-" + os.environ["FUZZER"], "trial-" + os.environ["TRIAL_ID"]), "sileo_sampling")
    # endregion: TO_GENERATE, fuzz_settings
    main_sileo_fuzzer.fuzz_inner(**kwargs)
