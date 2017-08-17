#!/usr/bin/env python3
"""
Compare the number of unique messages transmitted and received.
This is different than the number of unique frames because multiple frames
may contain duplicate message payloads.
"""

import binascii
import numpy
import struct

# Downlink files
downlink = "../command/downlink_33.16.log"
vtgs_rx = "../vtgs/VTGS_MAIN_20170813_093012.493395.log"
mgs_rx = "../mgs/MGS_MAIN_20170813_093034.453414.log"

# Load all of the unique FRAMES that were received
received = []
f = open(vtgs_rx)
f.readline() # Skip the first line always
for line in f:
    data = line.split(",")[2].strip()[20:]
    if data not in received:
        received.append(data)

f = open(mgs_rx)
f.readline()

for line in f:
    data = line.split(",")[2].strip()[20:]
    if data not in received:
        received.append(data)

print ("Total received unique messages: %d" % len(received))

# Try to get the full number of transmitted messages now
transmitted = []
f = open(downlink)
f.readline() # Skip the first line always
for line in f:
    data = line[48:].strip()[20:]
    if data not in transmitted:
        transmitted.append(data)

print ("Total transmitted unique messages: %d" % len(transmitted))
