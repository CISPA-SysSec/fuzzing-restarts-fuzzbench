import argparse
import concurrent.futures
import json
import pathlib
import subprocess
import tempfile
import zipfile
import re
import math
import hilbert
import tarfile
import io
import hashlib
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt
from collections import defaultdict
from threading import Lock
from pandas import DataFrame
from matplotlib.colors import LogNorm, Normalize

def gen_counts_from_path(cov_exe, prof_exe, llvm_cov_binary, zf, path, member_filename, profmerged):
    with tempfile.NamedTemporaryFile() as profdata:
        with tempfile.NamedTemporaryFile() as profraw:
            # run target to generate profraw
            subprocess.run([cov_exe, str(path)], env={'LLVM_PROFILE_FILE':profraw.name},
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # transform profraw to profdata
            subprocess.run([prof_exe, 'merge', '-sparse', profraw.name, '-o', profdata.name],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # merged
            #subprocess.run([prof_exe, 'merge', '-sparse',
            #               profraw.name, str(profmerged), '-o', str(profmerged)]
            #              )
            #               #stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            proc = subprocess.Popen([llvm_cov_binary, 'export', '-format=text',
                                     '-region-coverage-gt=0', '-skip-expansions', cov_exe,
                                     '-instr-profile={}'.format(profdata.name)],
                                    stdout=subprocess.PIPE)
            #proc = subprocess.Popen([prof_exe, 'show', '--all-functions', '--counts', tmpfile.name],
            outs, _ = proc.communicate()

    j = json.loads(outs.decode('ascii'))
    funcs = j['data'][0]['functions']
    #print(covered)
    data = []

    hit_true_index = 4
    hit_false_index = 5
    # The last number in the branch-list indicates what type of the
    # region it is; 'branch_region' is represented by number 4.
    type_index = -1
    branch_region_type = 4
    # The number of index 6 represents the file number.
    file_index = 6

    for f in funcs:
     
        extracted = []
        if not f['branches']:
            continue
        for branch in f['branches']:
            if branch[hit_true_index] != 0 or branch[ hit_false_index] != 0 and branch[type_index] == branch_region_type:
                extracted.append(branch[hit_true_index] != 0)
                extracted.append(branch[hit_false_index] != 0)
            else:
                extracted.append(False)
                extracted.append(False)

            #if branch[type_index] != branch_region_type:
            #    continue
            #extracted.append(branch[hit_false_index] != 0)
            
            #if branch[hit_true_index] != 0 or branch[hit_false_index] != 0:
            #    covered_branches.append(branch[:hit_true_index] + branch[file_index:])
        
        #if not branches:
        #    continue
        #last = branches.pop()
        #last = np.array(last) > 0
        #for b in branches:
        #    last |= np.array(b) > 0
        data.append((f['name'], extracted))

    with zf.open(member_filename, 'w') as fd:
        fd.write(json.dumps(data).encode('ascii'))


def gen_counts_from_sampling(cov_exe, prof_exe, llvm_cov_binary, trial):
    profmerged = trial / 'merged.profdata'
    profmerged.touch()
    if pathlib.Path(trial / 'lcov_sampling.zip').exists():
        return
    
    with zipfile.ZipFile(trial / 'lcov_sampling.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in trial.glob('sileo_sampling/*'):
            gen_counts_from_path(cov_exe, prof_exe, llvm_cov_binary, zf, path, path.name, profmerged)


def gen_counts_from_corpus(cov_exe, prof_exe, llvm_cov_binary, corpus):
    profmerged = corpus.parent.parent / 'merged.profdata'
    profmerged.touch()
    
    if pathlib.Path(corpus.parent.parent / 'lcov_corpus.zip').exists():
        return
    
    with zipfile.ZipFile(corpus.parent.parent / 'lcov_corpus.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        with tarfile.open(corpus, 'r:gz') as tar:
            all_digests = set()
            for member in tar.getmembers():
                if '/queue/' not in member.name or '/.state/' in member.name:
                    continue
                reader = tar.extractfile(member)
                if reader is None:
                    continue
                with tempfile.NamedTemporaryFile() as tmpfile:
                    blob = reader.read()
                    digest = hashlib.sha256(blob).hexdigest()
                    if digest in all_digests:
                        continue
                    all_digests.add(digest)
                    tmpfile.write(blob)
                    tmpfile.flush()
                    gen_counts_from_path(cov_exe, prof_exe, llvm_cov_binary, zf,
                                         pathlib.Path(tmpfile.name), digest, profmerged)


def lcov(parallel, coverage_binary, profdata_binary, llvm_cov_binary, folders):
    with concurrent.futures.ProcessPoolExecutor(max_workers=parallel) as executor:
        
        f_cnt = 1
        for f in folders:    
            t_cnt = 1
            print(f"Processing directory {t_cnt}/{len(folders)} ---- ({f.name})")
            for trial in f.glob(f'trial-*'):
                print(f"Processing sampling: {t_cnt}/{len(list(f.glob(f'trial-*')))}")
                #gen_counts_from_sampling(coverage_binary, profdata_binary, llvm_cov_binary, trial)
                executor.submit(gen_counts_from_sampling, coverage_binary, profdata_binary,
                                llvm_cov_binary, trial)
                t_cnt += 1
                
            t_cnt = 1
            for trial in f.glob(f'trial-*'):
                print(f"Processing corpus: {t_cnt}/{len(list(f.glob(f'trial-*')))}")
                t_cnt += 1
                # find latest corpus archive
                version = 0
                latest = None
                for c in list(trial.glob('corpus/corpus-archive-*.tar.gz')):
                    cversion = int(re.match(r'corpus-archive-([\d]+).tar.gz', c.name).group(1))
                    if cversion > version:
                        version = cversion
                        latest = c
                executor.submit(gen_counts_from_corpus, coverage_binary, profdata_binary,
                                llvm_cov_binary, latest)

def median(folders):
    target_name = ""
    for f in folders:
        trialToHitcount = {}
        for trial in f.glob('trial-*'):
            target_name = trial.parent.name.split("_")[0]
            funcToEdges = {}
            with zipfile.ZipFile(trial / 'lcov_corpus.zip', 'r') as zf:
                for name in zf.namelist():
                    blob = zf.read(name)
                    d = json.loads(blob)
                    for func, hitcounts in d:
                        if func not in funcToEdges:
                            funcToEdges[func] = np.array(hitcounts)
                        else:
                            funcToEdges[func] |= np.array(hitcounts)
            totalEdges = 0
            for edges in funcToEdges.values():
                totalEdges += len(edges[edges > 0])
            trialToHitcount[trial] = totalEdges

        d = sorted([(hitcount, t) for t, hitcount in trialToHitcount.items()])
        with open(f"median_{target_name}.txt","a") as fd:
            for idx, (hitcount, t) in enumerate(d):
                print('{}: hits {} {}'.format(idx, hitcount, t))
                fd.write(f'{idx}: hits {hitcount} {t}\n')


def load_trials(trials):
    trialToFuncs = {}
    trialToExecs = {}
    funcnameToLen = {}

    for trial in trials:
        funcToEdges = {}
        with zipfile.ZipFile(trial / 'lcov_sampling.zip', 'r') as zf:
            for name in zf.namelist():
                blob = zf.read(name)
                d = json.loads(blob)
                for func, hitcounts in d:
                    funcnameToLen[func] = len(hitcounts)
                    v = np.array(hitcounts).astype(int)
                    v[v > 0] = 1
                    if func not in funcToEdges:
                        funcToEdges[func] = v
                    else:
                        funcToEdges[func] += v
                trialToExecs.setdefault(trial, 0)
                trialToExecs[trial] += 1

        trialToFuncs[trial] = funcToEdges

    trialToVector = {}
    for trial in trialToFuncs.keys():
        trialToVector[trial] = []
    for funcname in funcnameToLen.keys():
        for trial, funcToEdges in trialToFuncs.items():
            v = funcToEdges.get(funcname)
            if v is None:
                v = np.array([0] * funcnameToLen[funcname])
            trialToVector[trial].append(v)
    for trial in trialToVector.keys():
        trialToVector[trial] = np.concatenate(trialToVector[trial])

    allEdges = sum(trialToVector.values())
    for trial, v in trialToVector.items():
        # only keep edges that are hit at least once in at least one trial
        v = v[allEdges > 0]
        trialToVector[trial] = v

    return trialToFuncs, trialToExecs, trialToVector

def edgeFrequencies(output, folders):
    target_name = ""

    all_trials = []
    folderToTrials = {}
    for folder in folders:
        folderToTrials[folder] = []
        for trial in folder.glob('trial-*'):
            target_name = trial.parent.name.split("_")[0]
            folderToTrials[folder].append(trial)
            all_trials.append(trial)

    trialToFuncs, trialToExecs, trialToVector = load_trials(all_trials)

    for trial, v in trialToVector.items():
        trialToVector[trial] = np.sort(v / trialToExecs[trial])

    legend_mapping = {
        'libpng_aflplusplus': 'AFL++',
        # Add more mappings as needed
    }

    # Assuming you have a dictionary that maps folder names to desired colors
    color_mapping = {
        'AFL++': 'tab:blue',
        "Sileo Corpus Pruning": "tab:orange",
        "Sileo Reset": "tab:red"        
    }


    df = DataFrame({'folder' : [], 'trial': [], 'edge': [], 'frequency': [], "colors": []})
    #df['colors'] = df['folder'].map(color_mapping)
    
    dfidx = 0
    for folder in folders:
        fuzzer_name = folder.name
        if "aflplusplus" in folder.name:
            fuzzer_name = "AFL++"
        elif "corpus" in folder.name:
            fuzzer_name = "Sileo Corpus Pruning"
        elif "_rnd_" in folder.name:
            fuzzer_name = "Sileo Reset"
            
        for trial in folderToTrials[folder]:
            for idx, frequency in enumerate(trialToVector[trial]):
                df.loc[dfidx] = [fuzzer_name, trial.name, idx, frequency, color_mapping[fuzzer_name]]
                dfidx += 1

    fig = plt.figure()
    p = sb.lineplot(data=df, errorbar=('pi', 80), x='edge', y='frequency', hue='folder', palette=color_mapping)
    p.set_yscale('log')
    fig.add_subplot(p)
    
    filename = f"freq_{target_name}.svg"
    fig.savefig(output / filename, bbox_inches='tight')

    df.reindex(frequency=df["frequency"][::-1])
    df.reindex(edge=df["edge"][::-1])

    fig2 = plt.figure()
    p = sb.lineplot(data=df, errorbar=('pi', 80), x='edge', y='frequency', hue='folder', palette=color_mapping)
    p.set_yscale('log')
    fig2.add_subplot(p)
    
    filename = f"freq_mir_{target_name}.svg"
    fig2.savefig(output / filename, bbox_inches='tight')


def heatmap(output, baseline, trials):
    trialToFuncs, trialToExecs, trialToVector = load_trials(trials + [baseline])

    for trial, v in trialToVector.items():
        trialToVector[trial] = v / trialToExecs[trial]

    baselineVec = trialToVector.pop(baseline)
    
    target_name = trials[0].parent.name.split("_")[0]

    with open(f"heatmap_values{target_name}.txt","w") as fd:
        
        for trial, v in trialToVector.items():
            trialToVector[trial] /= baselineVec
            trialToVector[trial][trialToVector[trial] == np.nan] = 1
            
            print('{}'.format(trial))
            print('{} entries larger 2'.format(sum(trialToVector[trial] > 2)))
            print('{} entries smaller 1/2'.format(sum(trialToVector[trial] < 1.0/2)))
            
            fd.write(f"{trial}\n")
            fd.write(f'{sum(trialToVector[trial] > 2)} entries larger 2\n')
            fd.write(f'{sum(trialToVector[trial] < 1.0/2)} entries smaller 1/2\n')
            

    denseLen = len(baselineVec)
    bitsToEncodeLen = math.log(denseLen, 2)
    dimensions = 2  # draw 2d image
    bitsPerDimension = bitsToEncodeLen / dimensions
    bitsPerDimension = math.ceil(bitsPerDimension)
    mapping = hilbert.decode(np.array(range(denseLen)), 2, bitsPerDimension)

    maxX = 0
    maxY = 0
    for idx in range(denseLen):
        x, y = mapping[idx]
        maxX = max(x, maxX)
        maxY = max(y, maxY)

    for trial, v in trialToVector.items():
        fig = plt.figure()
        cmap = sb.diverging_palette(230, 20, as_cmap=True)


        #histogram2d = np.zeros((int(maxX + 1), int(maxY + 1)))
        histogram2d = np.full((int(maxX + 1), int(maxY + 1)), np.inf)
        for idx, histentry in enumerate(v):
            histentry = min(histentry, 20)
            histentry = max(histentry, 1.0/20)
            x, y = mapping[idx]
            histogram2d[x][y] = histentry
        #histogram2d[histogram2d > 20] = 20
        #histogram2d[histogram2d < 1.0/20] = 1.0/20
        cmap.set_extremes(over="k")

        plot = sb.heatmap(histogram2d, square=True, norm=LogNorm(),
                          xticklabels=False, yticklabels=False, cmap=cmap, center=10, vmin=1.0/20, vmax=20)
        plot.set(xlabel=trial.name, ylabel='')
        fig.add_subplot(plot)

        target_name = trial.parent.name.split("_")[0]
        print(target_name)
        fuzzer_name = trial.parent.name.split("-")[1]
        print(fuzzer_name)
        filename = f"{target_name}_{fuzzer_name}_{trial.name}.svg"
        fig.savefig(output / filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True, dest='command')

    parser_lcov = subparsers.add_parser('lcov')
    parser_lcov.add_argument('-j', '--parallel', default=1, type=int)
    parser_lcov.add_argument('--coverage-binary', required=True, type=pathlib.Path)
    parser_lcov.add_argument('--profdata-binary', required=True, type=pathlib.Path)
    parser_lcov.add_argument('--llvm-cov-binary', required=True, type=pathlib.Path)
    parser_lcov.add_argument('folders', nargs='+', type=pathlib.Path)

    parser_median = subparsers.add_parser('median')
    parser_median.add_argument('folders', nargs='+', type=pathlib.Path)

    parser_frequency = subparsers.add_parser('frequency')
    parser_frequency.add_argument('--output', required=True, type=pathlib.Path)
    parser_frequency.add_argument('folders', nargs='+', type=pathlib.Path)

    parser_heatmap = subparsers.add_parser('heatmap')
    parser_heatmap.add_argument('--output', required=True, type=pathlib.Path)
    parser_heatmap.add_argument('--baseline', required=True, type=pathlib.Path)
    parser_heatmap.add_argument('trials', nargs='+', type=pathlib.Path)

    args = vars(parser.parse_args())
    command = args.pop('command')
    if command == 'lcov':
        lcov(**args)
    elif command == 'median':
        median(**args)
    elif command == 'frequency':
        edgeFrequencies(**args)
    elif command == 'heatmap':
        heatmap(**args)
