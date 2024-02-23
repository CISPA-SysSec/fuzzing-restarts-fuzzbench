import os
import threading

import yaml
from common import yaml_utils

_inited_exp_config = False
_inited_exp_config_lock = threading.Lock()
_EXTRA_DATA_FILESTORE: str = None
_ALLOW_OVERWRITE_EXISTING_EXP = False
_ONLY_KEEP_LAST_CORPUS = True
ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def init_exp_config():
    global _init_exp_config
    if not _inited_exp_config:
        _inited_exp_config_lock.acquire()
        for exp_config_fpath in ["config/experiment.yaml", 
                                 "src/config/experiment.yaml", 
                                 "/src/config/experiment.yaml", 
                                 os.path.join(os.environ.get("EXPERIMENT_FILESTORE", ""), os.environ.get("EXPERIMENT", ""), "input", "config/experiment.yaml")]:
            if os.path.exists(exp_config_fpath):
                read_config_from_exp_config(exp_config_fpath)
                break
        _inited_exp_config_lock.release()
        assert _inited_exp_config


def EXTRA_DATA_FILESTORE():
    init_exp_config()
    return _EXTRA_DATA_FILESTORE


def ALLOW_OVERWRITE_EXISTING_EXP():
    init_exp_config()
    return _ALLOW_OVERWRITE_EXISTING_EXP


def ONLY_KEEP_LAST_CORPUS():
    init_exp_config()
    return _ONLY_KEEP_LAST_CORPUS


def read_config_from_exp_config(config_filename):
    global _inited_exp_config
    _inited_exp_config = True
    config_read = yaml_utils.read(config_filename)
    kys = [k for k in config_read if k.startswith("sileo_")]
    for k in kys:
        match k:
            case "sileo_extra_data_filestore":
                global _EXTRA_DATA_FILESTORE
                _EXTRA_DATA_FILESTORE = config_read[k]
            case "sileo_allow_overwrite_existing_experiment":
                global _ALLOW_OVERWRITE_EXISTING_EXP
                _ALLOW_OVERWRITE_EXISTING_EXP = config_read[k]
                if not isinstance(_ALLOW_OVERWRITE_EXISTING_EXP, bool):
                    _ALLOW_OVERWRITE_EXISTING_EXP = str(
                        _ALLOW_OVERWRITE_EXISTING_EXP).lower() == 'true'
            case "sileo_only_keep_last_corpus":
                global _ONLY_KEEP_LAST_CORPUS
                _ONLY_KEEP_LAST_CORPUS = config_read[k]
                if not isinstance(_ONLY_KEEP_LAST_CORPUS, bool):
                    _ONLY_KEEP_LAST_CORPUS = str(
                        _ONLY_KEEP_LAST_CORPUS).lower() != 'false'

    return config_read


def get_fuzzer_yaml_config(fuzzer_name):
    yaml_fpath = os.path.join(ROOT_DIR, "fuzzers", fuzzer_name, "fuzzer.yaml")
    config = dict()
    if os.path.exists(yaml_fpath):
        with open(yaml_fpath, encoding="utf-8") as fin:
            config = yaml.load(fin, yaml.SafeLoader)
    return config


def get_files_regex_included_for_cov(fuzzer_name):
    config = get_fuzzer_yaml_config(fuzzer_name)
    return config.get("files_regex_included_for_cov", None)


def get_files_regex_excluded_for_cov(fuzzer_name):
    config = get_fuzzer_yaml_config(fuzzer_name)
    return config.get("files_regex_excluded_for_cov", None)


def get_files_regex_included_for_crashes(fuzzer_name):
    config = get_fuzzer_yaml_config(fuzzer_name)
    return config.get("files_regex_included_for_crashes", None)


def get_files_regex_excluded_for_crashes(fuzzer_name):
    config = get_fuzzer_yaml_config(fuzzer_name)
    return config.get("files_regex_excluded_for_crashes", None)
