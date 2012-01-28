#!/usr/bin/python

from collections import defaultdict, namedtuple
from functools import partial
from itertools import dropwhile, imap, takewhile
import os
import re
import sys

WHITE = re.compile(" +")
FRAME = re.compile(" +(.*)\.(.*)\(")
NUMSTART = re.compile("^ *[0-9]")

#  Oddments.

def partition_by(fn, seq):
    """Partition a sequence into a list of lists split each time fn(item) returns True"""
    def bucketize(lst, item):
        if len(lst) == 0 or fn(item):
            lst.append([item])
        else:
            lst[-1].append(item)
        return lst
    return reduce(bucketize, seq, [])

def comp(f): return lambda x: not f(x)
def untabify(s): return s.replace('\t', ' ')
def begins(prefix): return lambda s: s.startswith(prefix)
def chop(s): return s[0:-1]
def dict_by(seq, fn): return dict([(fn(x), x) for x in seq])

#  Represent HPROF data

class StackTrace:
    def __init__(self, tid, frames):
        self.tid, self.frames = tid, frames
    @staticmethod
    def parse(lines):
        header, frames = lines[0], lines[1:]
        frames = map(StackFrame.parse, frames)
        return StackTrace(int(header.split(" ")[1][0:-1]), frames)

class StackFrame:
    def __init__(self, klass, method):
        self.klass, self.method = klass, method
    def name(self):
        return self.klass + "." + self.method
    @staticmethod
    def parse(line):
        m = re.match(FRAME, line)
        return StackFrame(m.group(1), m.group(2))

class CPUSample:
    def __init__(self, count, percent, rank, tid):
        self.tid, self.rank, self.percent, self.count = tid, rank, percent, count
    @staticmethod
    def parse(line):
        a = re.split(WHITE, line.lstrip())
        return CPUSample(int(a[0]), float(chop(a[1])), int(a[3]), int(a[4]))

class Graph:
    """Simple adjacency-set representation of a DAG."""
    def __init__(self):
        self.V = set()
        self.E = {}
    def link(self, v1, v2):
        if not v1 in self.E:
            self.E[v1] = set()
        self.E[v1].add(v2)

def parse_hprof(stream):
    lines = (line.rstrip() for line in stream if not line.isspace())
    data = imap(untabify, dropwhile(comp(begins("-----")), lines))
    tracelines = takewhile(comp(begins("CPU SAMPLES BEGIN")), data)
    tracelines = dropwhile(comp(begins("TRACE")), tracelines)
    traces = map(StackTrace.parse, partition_by(begins("TRACE"), tracelines))
    samples = map(CPUSample.parse, filter(partial(re.match, NUMSTART), data))
    return dict_by(traces, lambda t: t.tid), dict_by(samples, lambda s: s.tid)

traces, samples = parse_hprof(sys.stdin)
accum = defaultdict(float)

for (tid, trace) in traces.items():
    done = set()
    for f in trace.frames:
        loc = f.name()
        if loc in done: continue
        accum[loc] += samples[tid].percent
        done.add(loc)

print sys.argv
if len(sys.argv) == 2:
    loc = sys.argv[1]
    dotree(loc)
else:
    x = sorted(accum.keys(), lambda a, b: cmp(accum[a], accum[b]))
    for y in x:
        print accum[y], y

