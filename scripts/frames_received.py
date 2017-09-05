#!/usr/bin/env python3
import binascii
import itertools
import numpy
import os
import struct

# Datasets
vtgs, mgs = [], []         # Frames received by each ground station
unique = []                # Unique frames received
vtgs_ids, mgs_ids = [], [] # Specific frame IDs recevied by each ground station
unique_ids = []

# Parse the log files and count the number of received frames by each station
f = open("../vtgs/VTGS_MAIN_20170813_093012.493395.log")
f.readline()    # Skip the first line because it is the logger initialization
for line in f:
    frame = line.split(",")[2].strip()
    vtgs.append(frame)
    if frame not in unique:
        unique.append(frame)
    # Get the id from the frame
    data = binascii.unhexlify(frame[12:16])
    frame_id = numpy.uint16(struct.unpack('>H', data))[0]
    vtgs_ids.append(frame_id)
    if frame_id not in unique_ids:
        unique_ids.append(frame_id)

f = open("../mgs/MGS_MAIN_20170813_093034.453414.log")
f.readline()
for line in f:
    frame = line.split(",")[2].strip()
    mgs.append(frame)
    if frame not in unique:
        unique.append(frame)
    # Get the id from the frame
    data = binascii.unhexlify(frame[12:16])
    frame_id = numpy.uint16(struct.unpack('>H', data))[0]
    mgs_ids.append(frame_id)
    if frame_id not in unique_ids:
        unique_ids.append(frame_id)

#-------------------------------------------------------------------------------
# Received frame statistics
v = len(vtgs)
m = len(mgs)

# Double check the number of total unique frames
union = list(set(vtgs_ids) | set(mgs_ids))
assert(len(union) == len(unique))

u = len(unique)
t = v + m
dup = v + m - u
p_dup = float((dup)/u)*100
p_v = float(v/u)*100
p_m = float(m/u)*100

print ("----------------------------------------")
print ("Received Frames:\n")
print ("Total       %d" % t)
print ("Unique      %d" % u)
print ("Duplicate   %4d (%.2f%%)" % (dup, p_dup))
print ("Vtgs        %4d (%.2f%%)" % (v, p_v))
print ("Mobile      %4d (%.2f%%)" % (m, p_m))
print ("----------------------------------------")

# Sort the unique id list to determine the last frame received
last = sorted(unique_ids)[-1]
print ("Expected Frames:\n")
print ("Last        %4d" % last)
missed = last - u
percent = float(missed / last) * 100
print ("Recevied    %4d (%.2f%%)" % (u, float(u / last) * 100))
print ("Missed      %4d (%.2f%%)" % (missed, percent))
print ("Vtgs        %.2f%%" % (float(v/last)*100))
print ("Mgs         %.2f%%" % (float(m/last)*100))
print ("Duplicate   %.2f%%" % (float((dup)/last)*100))
print ("----------------------------------------")

#-------------------------------------------------------------------------------
# Try to match the downlink log with the received frames
print ("Matching received frames with downlink...")

# Downlink files
files = os.listdir("../command")
downlinks = [os.path.join("../command", f) for f in files if "downlink" in f]

found = None
for down in downlinks:
    f = open(down)
    transmitted = []
    for line in f:
        # Skip the 'logger initialized' line
        if "Initialized" in line:
            continue
        transmitted.append(line[48:].strip())
    # Check if this downlink log has the same frames that were received
    if set(unique) < set(transmitted):
        print ("Found downlink: %s" % down)
        found = down
        break
    else:
        transmitted = []
if not found:
    print ("Unable to match the downlink log with the received frames...")
    exit()

# Build a list of transmitted frame IDs to compare against the received IDs
transmitted_ids = []
for frame in transmitted:
    data = binascii.unhexlify(frame[12:16])
    frame_id = numpy.uint16(struct.unpack('>H', data))[0]
    transmitted_ids.append(frame_id)

print ("----------------------------------------")
last = sorted(transmitted_ids)[-1]
print ("Transmitted Frames:\n")
print ("Total       %4d" % last)
missed = last - u
percent = float(missed / last) * 100
print ("Recevied    %4d (%.2f%%)" % (u, float(u / last) * 100))
print ("Missed      %4d (%.2f%%)" % (missed, percent))
print ("Vtgs        %.2f%%" % (float(v/last)*100))
print ("Mgs         %.2f%%" % (float(m/last)*100))
print ("Duplicate   %.2f%%" % (float((dup)/last)*100))
print ("----------------------------------------")

#-------------------------------------------------------------------------------
# Print out a list of missed frames based on ranges.
missed_ids = sorted(list(set(transmitted_ids) - set(unique_ids)))
print ("Missed Frames:\n")

missed_list = []
base = missed_ids[0]
prev = missed_ids[0]
count_missed = 0
for i in missed_ids[1:]:
    # If current == prev+1 it is still in the same range:
    #   Save the current as prev and continue
    # Otherwise, a new range has started:
    #   Append the new range, save i as the base and prev, and continue.
    # At the end of the list, always save the final range
    if i != (prev + 1):
        # New Range!
        if base == prev:
            missed_list.append("%d" % base)
            count_missed += 1
        else:
            missed_list.append("%d-%d" % (base, prev))
            count_missed = count_missed + (prev - base + 1)
        base = i
    prev = i
# Always save the last range
if base == prev:
    missed_list.append("%d" % base)
    count_missed += 1
else:
    missed_list.append("%d-%d" % (base, prev))
    count_missed = count_missed + (prev - base + 1)

print (", ".join(missed_list).join('[]'))
print (count_missed)
print ("----------------------------------------")
