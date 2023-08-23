from itertools import tee, zip_longest
import traverse
import random
import pickle
import sys
import re

no_empty   = lambda lst: filter(bool, lst)
map_filter = lambda f, lst: list(no_empty(map(f, lst)))
clean_word = lambda s: s.lower().strip(".?!…,;«»“”—–-:'\"()_")
process    = lambda s: map_filter(clean_word, re.split('\s+', s.strip().lower()))
join       = lambda xs: " ".join(xs)

def pairs(it):
    fst, snd = tee(it)

    try:
        next(snd)
        return zip(fst, snd)
    except StopIteration:
        return []

def group(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def markovify(kv, sources):
    for (prev, curr) in pairs(sources):
        if prev not in kv: kv[prev] = {}
        kv[prev][curr] = kv[prev].get(curr, 0) + 1

    return kv

def learn(chunk, strings):
    kv = {}
    for line in strings:
        words = map(join, group(process(line), chunk, fillvalue=""))
        try:
            kv = markovify(kv, words)
        except StopIteration:
            pass
    return kv

def learn_text(chunk, filename):
    with open(filename, 'r', encoding='utf-8') as fin:
        return learn(chunk, [fin.read()])

def learn_csv(chunk, filename):
    return learn(chunk, traverse.messages(filename))

teachers = { "txt": learn_text, "csv": learn_csv }

try:
    _, input, mode, output, chunk = sys.argv

    if mode not in ["txt", "csv"]:
        raise ValueError()
    chunk = int(chunk)
except ValueError:
    print("Usage: {} input [txt|csv] output chunk-size".format(sys.argv[0]))
    sys.exit(-1)

with open(output, 'wb') as fout:
    pickle.dump(teachers[mode](chunk, input), fout)
