#!/usr/bin/python
# coding=utf-8

from scapy.all import *

import argparse

from scapy.layers.inet import IP, UDP, ICMP, TCP
from scapy.layers.l2 import Ether, Dot1Q
"""
profile address-table "tun"
s-vlan 200 use c-vlan
s-vlan 300 use c-vlan
s-vlan 10 use c-vlan
exit

profile cross-connect "sel_tun_1"
bridge
bridge group "40"
tag-mode selective-tunnel
outer vid "200"
exit
profile cross-connect "sel_tun_2"
bridge
bridge group "40"
tag-mode selective-tunnel
outer vid "300"
exit
profile cross-connect "tun"
bridge
bridge group "40"
tag-mode tunnel
outer vid "10"
exit
profile cross-connect "sing80_80"
bridge
bridge group "40"
outer vid "80"
user vid "80"
exit
profile cross-connect "sing50_60"
bridge
bridge group "40"
outer vid "50"
user vid "60"
exit
profile ports "test"
port    0 bridge group "40"
exit
interface ont 3/3
serial "ELTX6201D46C"
service 1 profile cross-connect "sel_tun_1"
service 1 profile dba "dba-00"
service 3 profile cross-connect "sel_tun_2"
service 3 profile dba "dba-00"
service 0 profile cross-connect "tun"
service 0 profile dba "dba-00"
service 1 profile cross-connect "sing50_60"
service 1 profile dba "dba-00"
profile ports "test"
service    1 selective-tunnel uvid 100-105
service    2 selective-tunnel uvid 106-108
exit
exit
commit
switch
configure
vlan 10
name VLAN0010
tagged front-port 1
tagged pon-port 3
exit
vlan 50
name VLAN0050
tagged front-port 1
tagged pon-port 3
exit
vlan 80
name VLAN0080
tagged front-port 1
tagged pon-port 3
exit
vlan 200
name VLAN0200
tagged front-port 1
tagged pon-port 3
exit
vlan 300
name VLAN0300
tagged front-port 1
tagged pon-port 3
exit
commit  

"""


interface = 'eth0'
verbose = False
pktNum = 0

def create_parser():
    p = argparse.ArgumentParser()
    p.add_argument('-u', '--upstream', action='store_true')
    p.add_argument('-d', '--downstream', action='store_true')
    p.add_argument('-i', '--iface', type=str, default=interface)
    return p

def gen(pkt):
    global pktNum
    global passed
    global dropped
    pkt[Raw].load = ('{:02}|' + pkt[Raw].load).format(pktNum + 1)
    pktNum += 1
    sendp(pkt, iface=interface, verbose=verbose)
    if pkt[Raw].load.find('PASS') == -1:
        dropped += 1
    else:
        passed += 1
    return pkt[Raw].load

def printStat():
    print "\nResult:\n   Total: {:3}\n    Pass: {:3}\n\n".format(passed+dropped, passed)

def pauseOn(condition):
    if condition:
        print 'Press enter to continue'
        sys.stdin.readline()


def upstreamTest():
    print 'send selective tunnel service 0 packets upstream 100-105'
    for p in (100,101,102,103,104,105):
        gen(eth / Dot1Q(vlan=p) / ip / udp / "PASS-sel tunnel 0".format(p))
    
    print 'send selective tunnel service 1 packets upstream 106-108'
    for p in (106,107,108):
        gen(eth/ Dot1Q(vlan=p) / ip / udp / "PASS-sel tunnel 1".format(p))

    print 'send tunnel service 2 packets upstream 109-115'
    for p in (109,110,111,112,113,114):
        gen(eth / Dot1Q(vlan=p) / ip / udp / "PASS-common tunnel".format(p))
    print 'send single-tag services packets upstream'
    for p in (80,60):
        gen(eth / Dot1Q(vlan=p) / ip / udp / "PASS-single tag upstream".format(p))


def downstreamTest():
    print 'send selective tunnel service 0 packets downstream 200/100-105'
    for p in (100, 101, 102, 103, 104, 105):        
        gen(ethDown / Dot1Q(vlan=200) / Dot1Q(vlan=p) / ipDown / udp / "PASS-sel tunnel 0 downstream".format(p))

    print 'send selective tunnel service 1 packets downstream 300/106-108'
    for p in (106, 107, 108):
        gen( ethDown / Dot1Q(vlan=300) / Dot1Q(vlan=p) / ipDown / udp / "PASS-sel tunnel 1 downstream".format(p))

    print 'send tunnel service 2 packets downstream 10/109-115'
    for p in (109, 110, 111, 112, 113, 114):
        gen(ethDown / Dot1Q(vlan=10) / Dot1Q(vlan=p) / ipDown / udp / "PASS-common tunnel downstream".format(p))
    print 'send single-tag services packets downstream'
    for p in (80, 50):
        gen(ethDown / Dot1Q(vlan=p) / ipDown / udp / "PASS-single tag downstream".format(p))


if __name__ == '__main__':
    passed = 0
    dropped = 0
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])
    interface = args.iface

    eth = Ether(src='A8:F9:4B:BB:00:01', dst='A8:F9:4B:BB:00:02')
    ethDown = Ether(src='A8:F9:4B:BB:00:02', dst='A8:F9:4B:BB:00:01')
    vlan = Dot1Q(vlan=5)
    ip = IP(src='1.1.1.0', dst='2.2.2.0')
    ipDown = IP(dst='2.2.2.0', src='1.1.1.0')
    udp = UDP(sport=1234, dport=5678)
    tcp = TCP(sport=1234, dport=5678)


    if args.upstream:
        upstreamTest()
    elif args.downstream:
        downstreamTest()


    printStat()