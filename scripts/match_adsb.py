#!/usr/bin/env python3
"""
Try to match the ADSB log files to the messages received by VTGS and MGS
"""

import binascii
import numpy
import struct
import os

payload = "../payload"
files = os.listdir(payload)
adsb_files = [os.path.join(payload, f) for f in files if "adsb" in f]

# Get all of the adsb messages we received:
adsb_output = "../vtgs/VTGS_ADSB_MSG_20170813_093012.493395.log"
f = open(adsb_output)
adsb_messages = []
f.readline()
for line in f:
    msg = line.split(',')[-1].strip()
    if msg not in adsb_messages:
        adsb_messages.append(msg)
#print ("Unique adsb: %d" % len(adsb_messages))

# Try to figure out the number of unique messages received by the entire system
# Go through all the lines received. If any are missing, it's the wrong file
for payload in adsb_files:
    f = open(payload)
    f.readline()
    transmitted = []
    for line in f:
        transmitted.append(line[54:].strip().split()[0])
    if (set(adsb_messages) & set(transmitted)):
        print ("Found downlink: %s" % payload)
