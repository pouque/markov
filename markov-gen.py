from itertools import tee
import random
import pickle
import chlor
import sys
import re

def no_empty(lst):
    return filter(bool, lst)

def map_filter(f, lst):
    return list(no_empty(map(f, lst)))

def clean_word(s):
    return s.lower().strip(',;«»-"()')

def process(s):
    return map_filter(clean_word, re.split('\s+', s.strip().lower()))

def markovify(kv, text):
    fst, snd = tee(text)
    next(snd)

    for (prev, curr) in zip(fst, snd):
        if prev not in kv: kv[prev] = {}
        kv[prev][curr] = kv[prev].get(curr, 0) + 1

    return kv

def learn(strings):
    kv = {}
    for line in strings:
        words = process(line)
        if len(words) > 1:
            kv = markovify(kv, words)
    return kv

def learn_text(filename):
    with open(filename, 'r', encoding='utf-8') as fin:
        return learn([fin.read()])

def learn_csv(filename):
    return learn(chlor.messages(filename))

teachers = { "txt": learn_text, "csv": learn_csv }

try:
    _, input, mode, output = sys.argv

    if mode not in ["txt", "csv"]:
        raise ValueError()
except ValueError:
    print("Usage: {} input [txt|csv] output".format(sys.argv[0]))
    sys.exit(-1)

with open(output, 'wb') as fout:
    pickle.dump(teachers[mode](input), fout)