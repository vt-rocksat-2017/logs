#!/usr/bin/env python3
import binascii
import itertools
import numpy
import os
import struct

from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from scipy.interpolate import spline

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
print ("Missed Frames:\n")
def generate_ranges(ids):
    # This takes a list of IDs and returns a list of ranges (i.e. 34-56, 59-80)
    # IDs that do not belong to a range are returned as single elements
    # Example: [3, 4, 6, 7, 8, 10, 12] -> [3, 4], [6, 8], 10, 12
    tmp = []
    base, prev = ids[0], ids[0]
    for i in ids[1:]:
        # If current == prev+1 it is still in the same range:
        #   Save the current as prev and continue
        # Otherwise, a new range has started:
        #   Append the new range, save i as the base and prev, and continue.
        # At the end of the list, always save the final range
        if i != (prev + 1):
            tmp.append([base, prev]) if base != prev else tmp.append(base)
            base = i
        prev = i
    # Don't forget the final range/value
    tmp.append([base, prev]) if base != prev else tmp.append(base)
    return tmp

missed_ids = sorted(list(set(transmitted_ids) - set(unique_ids)))
assert (len(missed_ids) == missed)
missed_ranges = generate_ranges(missed_ids)
print (missed_ranges)
print ("----------------------------------------")


#-------------------------------------------------------------------------------
print ("Plotting ground station access times...")

# Generate the line segments and points that represent the access time
def generate_access_time_plot_from_range(id_range, val):
    """
    Takes an input range from generate_ranges and creates line segments and
    data points to represent access times.
    """
    segments = []
    points = []

    for i in id_range:
        if isinstance(i, list):
            endpoints = [(i[0], val), (i[1], val)]
            segments.append(endpoints)
        else:
            points.append((i, val))
    return segments, points

# Generates X/Y plots
def generate_access_time_plot(id_lists):
    """
    Takes multiple lists of ids, and generates X/Y points representing access time
    """
    bins = [1]
    points = []
    for l in id_lists:
        mapped = [(x, bins[-1]) for x in l]
        points += mapped
        bins.append(bins[-1] + 1)
    return points, bins

# Generate the scatter plot points for the access times
points, bins = generate_access_time_plot([vtgs_ids, mgs_ids, missed_ids])

# Generate the plot using the ranges to build line collections
fig, ax = plt.subplots()
ax = plt.axes()
ax.set_xlim((0, transmitted_ids[-1]))
ax.set_ylim((0, len(bins)))
ax.set_title("Ground Station Access Times")

labels = ['VTGS', 'MGS', 'Missed']
ax.set_yticks(bins)
ax.set_yticklabels(labels, fontsize="12")
plt.xlabel("Frame ID")

'''
# Line segment based version
vtgs_ranges = generate_ranges(vtgs_ids)
vtgs_segments, vtgs_points = generate_access_time_plot_from_range(vtgs_ranges, 1)

mgs_ranges = generate_ranges(mgs_ids)
mgs_segments, mgs_points = generate_access_time_plot_from_range(mgs_ranges, 2)

missed_ranges = generate_ranges(missed_ids)
missed_segments, missed_points = generate_access_time_plot_from_range(missed_ranges, 3)

all_segments = vtgs_segments + mgs_segments + missed_segments
all_points = vtgs_points + mgs_points + missed_points

[x, y] = list(zip(*all_points))
segments = LineCollection(all_segments, linestyles='solid')
ax.add_collection(segments)
ax.scatter(x, y, s=1)
'''

[x, y] = list(zip(*points))
ax.scatter(x, y, s=2)

# Calculate the percentage of missed packets for the past 100 packets
length = 100
percents = [1.0] * length
for i in range(length, transmitted_ids[-1]):
    ids = set(range(i, i + length))
    received_window = list(ids.intersection(set(unique_ids)))
    percents.append(float(len(received_window) / length))
x2 = range(transmitted_ids[-1])

ax2 = ax.twinx()
ax2.plot(x2, percents, 'r-')
ax2.set_ylabel('Percent Received (Past %d)' % length, color='r')
ax2.tick_params('y', colors='r')

plt.show()
