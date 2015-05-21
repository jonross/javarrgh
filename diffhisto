#!/usr/bin/python

from collections import namedtuple
import os, re, sys

if len(sys.argv) != 3:
    sys.stderr.write("Need 2 histo files\n")
    sys.exit(1)

Slot = namedtuple("Slot", "count bytes classname")

def parse(line):
    fields = line.split()[1:]
    return Slot(int(fields[0]), int(fields[1]), fields[2])

def slots(filename):
    finder = re.compile("^ *\\d+:")
    return (parse(line) for line in open(filename) if finder.match(line))

h1 = {slot.name : slot for slot in slots(sys.argv[1]) }
h2 = {slot.name : slot for slot in slots(sys.argv[2]) }

h1.update({name: Slot(0, 0, name) for name in h2 if name not in h1})
h2.update({name: Slot(0, 0, name) for name in h1 if name not in h2})

def delta(s1, s2):
    return Slot(s2.count - s1.count, s2.bytes - s1.bytes, s1.classname)

h3 = [delta(h1[classname], h2[classname]) for classname in h1.keys()]
h3.sort(lambda s1, s2: abs(s1.bytes) - abs(s2.bytes), None, True)

total = sum([abs(slot.bytes) for slot in h3])

def pad(value, fmt, width):
    return (fmt % value).rjust(width)

cum = 0
print "  pct    cum %10s %12s  %s" % ("count", "bytes", "class")
for slot in h3:
    cum += abs(slot.bytes)
    pct = 1.0 * abs(slot.bytes) / total * 100
    cumpct = 1.0 * cum / total * 100
    print "%s%%  %s%% %10d %12d  %s" % (
            pad(pct, "%.1f", 4), pad(cumpct, "%.1f", 4),
            slot.count, slot.bytes, slot.classname)
