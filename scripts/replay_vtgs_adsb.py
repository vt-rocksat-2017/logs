#!/usr/bin/env python3
"""
Replay the ADSB messages in the VTGS log
"""

import binascii

from socket import *

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(("127.0.0.1", 30003))

adsb_output = "../vtgs/VTGS_ADSB_MSG_20170813_093012.493395.log"
f = open(adsb_output)
f.readline()
for line in f:
    msg = line.split(',')[-1].strip()
    print ("'%s'" % msg)
    fixed = "*%s;\n" % msg
    sock.send(fixed.encode('utf-8'))
    #sock.send()
