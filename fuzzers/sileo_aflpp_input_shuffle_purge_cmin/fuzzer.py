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
    kwargs["sileo_mode"] = 'input_shuffle'
    kwargs["sileo_purge"] = 'purge'
    kwargs["sileo_rtime"] = '5m-30m'
    kwargs["sileo_cmin"] = True
    # endregion: TO_GENERATE, fuzz_settings
    main_sileo_fuzzer.fuzz_inner(**kwargs)
