#!/usr/bin/python

from collections import namedtuple
import os, re, sys

if len(sys.argv) != 3:
    sys.stderr.write("Need 2 histo files\n")
    sys.exit(1)

HISTO = re.compile("^ *\\d+:")
WHITE = re.compile("[ \t]+")

HistoEntry = namedtuple("HistoEntry", "count bytes classname")

def readhisto(filename):
    histo = {}
    for line in open(filename):
	if HISTO.match(line):
	    fields = re.split(WHITE, line.strip())[1:]
	    entry = HistoEntry(int(fields[0]), int(fields[1]), fields[2])
	    histo[entry.classname] = entry
    return histo

h1 = readhisto(sys.argv[1])
h2 = readhisto(sys.argv[2])

def reconcile(h1, h2):
    for classname in h1:
	if classname not in h2:
	    h2[classname] = HistoEntry(0, 0, classname)

reconcile(h1, h2)
reconcile(h2, h1)

def delta(h1, h2):
    return HistoEntry(h2.count - h1.count, h2.bytes - h1.bytes, h1.classname)

h3 = [delta(h1[classname], h2[classname]) for classname in h1.keys()]

def compare(h1, h2):
    if h1.bytes != h2.bytes:
	return h1.bytes - h2.bytes
    if h1.count != h2.count:
	return h1.count - h2.count
    return 0

h3.sort(compare, None, True)

print "%10s%12s  %s" % ("count", "bytes", "class")
for entry in h3:
    print "%10d%12d  %s" % (entry.count, entry.bytes, entry.classname)
