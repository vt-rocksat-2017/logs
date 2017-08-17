#!/usr/bin/env python3
import binascii
import itertools
import numpy
import struct

from operator import itemgetter
from itertools import groupby

# Datasets
vtgs = []
mgs = []
vtgs_ids = []
mgs_ids = []

# Count the combined number of received frames from the VTGS and MGS
f = open("../vtgs/VTGS_MAIN_20170813_093012.493395.log")
for line in f:
    data = line.split(",")
    if len(data) > 2:
        m = data[2]
        vtgs.append(m)
        d = binascii.unhexlify(m[12:16])
        dn_pkt_id = numpy.uint16(struct.unpack('>H', d))[0]
        vtgs_ids.append(dn_pkt_id)

f = open("../mgs/MGS_MAIN_20170813_093034.453414.log")
for line in f:
    data = line.split(",")
    if len(data) > 2:
        m = data[2]
        mgs.append(m)
        d = binascii.unhexlify(m[12:16])
        dn_pkt_id = numpy.uint16(struct.unpack('>H', d))[0]
        mgs_ids.append(dn_pkt_id)

# Try to figure out the number of unique messages received by the entire system
v = len(vtgs)
m = len(mgs)

# Figure out stats
print ("Number of packets received:")
print ("Vtgs      : %d" % v)
print ("Mobile    : %d" % m)
print ("-----")

# Total?
union = list(set(vtgs_ids) | set(mgs_ids))
t = len(union)
dup = v + m - t
print ("Both      : %d" % t)
print ("Duplicate : %d" % dup)
print ("-----")

print ("(Percentage of the TOTAL frames that were seen)")
print ("Pct Vtgs  : %f" % (float(v/t)*100))
print ("Pct Mgs   : %f" % (float(m/t)*100))
print ("Dup Seen  : %f" % (float((dup)/t)*100))
print ("-----")

# Assume the LAST element is the largest id
last = union[-1]
print ("Expected  : %d (Based on last message recevied)" % last)
missed = last - t
percent = float(missed / last) * 100
print ("Recevied  : %d (%f)" % (t, float(t / last) * 100))
print ("Missed    : %d (%f)" % (missed, percent))
print ("-----")

print ("(Percentage of the EXPECTED frames that were seen)")
print ("Pct Vtgs  : %f" % (float(v/last)*100))
print ("Pct Mgs   : %f" % (float(m/last)*100))
print ("Dup Seen  : %f" % (float((dup)/last)*100))
print ("-----")

all_ids = range(last)
missed_ids = sorted(list(set(all_ids) - set(union)))

def get_ranges(ls):
    N = len(ls)
    while ls:
        # single element remains, yield the trivial range
        if N == 1:
            yield range(ls[0], ls[0] + 1)
            break

        diff = ls[1] - ls[0]
        # find the last index that satisfies the determined difference
        i = next(i for i in range(1, N) if i + 1 == N or ls[i+1] - ls[i] != diff)

        yield range(ls[0], ls[i] + 1, diff)

        # update variables
        ls = ls[i+1:]
        N -= i + 1

print ("Missed Ids:")
print (missed_ids)
# Rewrite the above function to produce better ranges
#for r in get_ranges(missed_ids):
#   print (r)
