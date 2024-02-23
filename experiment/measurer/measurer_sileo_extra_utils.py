import hashlib
import os
import shutil
import time

from common import logs
logger = logs.Logger()
ENABLE_SILEO_FILTER = False
ENABLE_SILEO_SHADOW_FILTER = False # if enabled, we filter possible inputs using fstats then hash, otherwise we only use hash
MIN_CORPUS_NUM_PER_SHARE = 100


def fpath2sileo_hash(hash_digester, fpath):
    """LALALA, designed for corpus_del"""
    res = []
    with open(fpath, "rb") as fin:
        content = fin.read()
        res.append(hex(len(content)))
        res.append("_")
        hash_digester.update(content)
        res.append(hash_digester.digest().hex())
        if len(content) > 512:
            hash_digester.update(content[:512])
            res.append(hash_digester.digest().hex())
        return "".join(res)

def deep_filter4sileo_filter_inputs_redundancy4coverage(fpaths, _, meta_dir):
    """LALALA, we filter those inputs again using hash that have been recorded in sileo_evaled4coverage_hash.txt"""
    hash_digester = hashlib.md5()
    record_fpath = os.path.join(meta_dir, "sileo_evaled4coverage_hash.txt")
    my_hash_set = set()
    allowed_fpaths_and_hash_prs = []
    if os.path.exists(record_fpath):
        with open(record_fpath, "r") as fin:
            my_hash_set = set([line.strip() for line in fin.readlines() if len(line) > 0])
        logger.info(f"Read {len(my_hash_set)} records from record_fpath {record_fpath}")
    org_set_len = len(my_hash_set)
    for fpath in fpaths:
        if fpath == record_fpath:
            continue
        hash_new = fpath2sileo_hash(hash_digester, fpath)
        if hash_new in my_hash_set:
            continue
        else:
            my_hash_set.add(hash_new)
            allowed_fpaths_and_hash_prs.append((fpath, hash_new))
    if len(my_hash_set) != org_set_len:
        with open(record_fpath, "w") as fout:
            fout.write("\n".join(my_hash_set))
    return allowed_fpaths_and_hash_prs


def shadow_filter4sileo_filter_inputs_redundancy4coverage(fpaths, org_corpus_dir, meta_dir):
    """LALALA, we filter possible inputs if those inputs have been recorded in sileo_evaled4coverage_fstat.txt"""
    record_fpath = os.path.join(meta_dir, "sileo_evaled4coverage_fstat.txt")
    my_info_set = set()
    allowed_fpaths = []
    if os.path.exists(record_fpath):
        with open(record_fpath, "r") as fin:
            my_info_set = set([line.strip() for line in fin.readlines() if len(line) > 0])
        logger.info(f"Read {len(my_info_set)} records from record_fpath {record_fpath}")
    my_info_set_new = set(my_info_set)
    for fpath in fpaths:
        if fpath == record_fpath:
            continue
        fd_in = os.open(fpath, os.O_RDONLY)
        a_fstats = os.fstat(fd_in)
        info = f"{os.path.relpath(fpath, org_corpus_dir)}_{a_fstats.st_size}"
        os.close(fd_in)
        if info not in my_info_set:
            my_info_set_new.add(info)
            allowed_fpaths.append(fpath)
    if len(my_info_set) != len(my_info_set_new):
        with open(record_fpath, "w") as fout:
            fout.write("\n".join(my_info_set_new))
    return allowed_fpaths


def sileo_filter_inputs_redundancy4coverage(org_corpus_dir, tmp_corpus_dir, meta_dir):
    if not ENABLE_SILEO_FILTER:
        return org_corpus_dir
    if os.path.exists(tmp_corpus_dir):
        shutil.rmtree(tmp_corpus_dir)
    os.makedirs(tmp_corpus_dir)
    if not os.path.exists(meta_dir):
        os.makedirs(meta_dir)
    start_time = time.time()
    fpaths = [os.path.join(root, fname) for root, _, fnames in os.walk(org_corpus_dir) for fname in fnames]
    logger.info(f"LALALA:sileo_filter_inputs_redundancy4coverage started, trying to filter {len(fpaths)} files from {org_corpus_dir}")
    if ENABLE_SILEO_SHADOW_FILTER:
        fpaths = shadow_filter4sileo_filter_inputs_redundancy4coverage(fpaths, org_corpus_dir, meta_dir)
    allowed_fpaths_and_hash_prs = deep_filter4sileo_filter_inputs_redundancy4coverage(fpaths, org_corpus_dir, meta_dir)
    for (fpath, hash_new) in allowed_fpaths_and_hash_prs:
        shutil.copy(fpath, os.path.join(tmp_corpus_dir, hash_new))
    logger.info(f"LALALA:sileo_filter_inputs_redundancy4coverage done, {len(allowed_fpaths_and_hash_prs)} files remained, used {time.time() - start_time} seconds")
    return tmp_corpus_dir

def reset_filter4sileo_filter_inputs_redundancy4coverage(meta_dir):
    logger.warning(f"reset_filter4sileo_filter_inputs_redundancy4coverage, meta_dir: {meta_dir}...")
    for fname in ["sileo_evaled4coverage_fstat.txt", "sileo_evaled4coverage_hash.txt"]:
        fpath = os.path.join(meta_dir, fname)
        if os.path.exists(fpath):
            os.remove(fpath)

def get_meta_sileo_filter_inputs_redundancy4coverage_dir(corpus_dir):
    """usually, corpus_dir will be cleared every cycle"""
    return os.path.join(os.path.dirname(corpus_dir), "meta_sileo_filter_inputs_redundancy4coverage")


def get_tmp_sileo_filter_inputs_redundancy4coverage_dir(corpus_dir):
    """usually, corpus_dir will be cleared every cycle"""
    return os.path.join(corpus_dir, "tmp_sileo_filter_inputs_redundancy4coverage")


def split_corpus_dir(corpus_dir, max_job_num):
    fpaths = [os.path.join(root, fname) for root, _, fnames in os.walk(corpus_dir) for fname in fnames]
    job_num = min(max_job_num, int((len(fpaths) + MIN_CORPUS_NUM_PER_SHARE - 1) / MIN_CORPUS_NUM_PER_SHARE))
    sub_corpus_dirs = []
    for i in range(job_num):
        sub_corpus_dir = os.path.join(corpus_dir, str(i))
        sub_corpus_dirs.append(sub_corpus_dir)
        if not os.path.exists(sub_corpus_dir):
            os.makedirs(sub_corpus_dir)
    for i, fpath in enumerate(fpaths):
        sub_corpus_dir = sub_corpus_dirs[i % job_num]
        newfpath = os.path.join(sub_corpus_dir, os.path.relpath(fpath, corpus_dir))
        if not os.path.exists(os.path.dirname(newfpath)):
            os.makedirs(os.path.dirname(newfpath))
        os.rename(fpath, newfpath)
    
    return job_num, sub_corpus_dirs
