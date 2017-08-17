#!/usr/bin/env python3
"""
Determine which log file(s) match the downlink received by VTGS and MGS
"""

import binascii
import numpy
import struct
import os

# Downlink files
files = os.listdir("../command")
downlinks = [os.path.join("../command", f) for f in files if "downlink" in f]

# Load all the packets we did received
received = []
f = open("../vtgs/VTGS_MAIN_20170813_093012.493395.log")
f.readline() # Skip the first line always
for line in f:
    data = line.split(",")[2].strip()
    if data not in received:
        received.append(data)

f = open("../mgs/MGS_MAIN_20170813_093034.453414.log")
f.readline()
for line in f:
    data = line.split(",")[2].strip()
    if data not in received:
        received.append(data)

print ("Total received: %d" % len(received))

# Try to figure out the number of unique messages received by the entire system
# Go through all the lines received. If any are missing, it's the wrong file
for down in downlinks:
    f = open(down)
    f.readline()
    transmitted = []
    for line in f:
        transmitted.append(line[48:].strip())
    if set(received) < set(transmitted):
        print ("Found downlink: %s" % down)
        found = down
        break

# Parse the data from that
ids = []
for t in transmitted:
    d = binascii.unhexlify(t[12:16])
    dn_pkt_id = numpy.uint16(struct.unpack('>H', d))[0]
    ids.append(dn_pkt_id)

print ("Transmitted data:")
print ("Frames: %d" % len(ids))
