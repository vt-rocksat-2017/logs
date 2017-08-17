#!/usr/bin/env python3
"""
Opens all of the adsb log files in the payload directory and sends
the captured messages to Virtual Server
"""

import binascii
import os

from socket import *

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(("127.0.0.1", 30003))

payload = "../payload"
files = os.listdir(payload)

adsb_files = [os.path.join(payload, f) for f in files if "adsb" in f]

# Send all of the captured ADSB messages to Virtual Server
for payload in adsb_files:
    f = open(payload)
    f.readline()
    transmitted = []
    for line in f:
        #transmitted.append(line[54:].strip().split()[0])
        msg = line[54:].strip().split()[0]
        fixed = "*%s;\n" % msg
        sock.send(fixed.encode('utf-8'))
