#! /usr/bin/python2.7
import argparse
import re
import commands
import time
import sys
import pexpect
import Exscript
from Exscript import  Account
from Exscript.protocols import *
from Exscript.protocols.drivers.driver import Driver


def createParser():
    p = argparse.ArgumentParser()
    p.add_argument('-i', '--ipaddr', default='192.168.199.155')
    return p


class OLTClishDriver(Driver):
    def __init__(self):
        Driver.__init__(self, "OLTClishDriver")
        self.user_re = [re.compile(r"login: ")]
        self.password_re = [re.compile(r"Password: $")]
        self.prompt_re = [re.compile(r"[\r\n]?\S+\(?\S*\)?# ?$"),
                          re.compile(r"[\r\n]?\(acs-?.*\)$")]
        clish_errors = [r"error",
                        r"invalid",
                        r"Revision failed",
                        r"unknown command",
                        r"connection timed out",
                        r"the command is not completed",
                        r"[^\r\n]+ not found"]
        self.error_re = [re.compile(r"^%?\s*(?:" + "|".join(clish_errors)
                                    + r")", re.I)]
        self.login_error_re = [
            re.compile(r"[\r\n]?\s*(?:incorrect|available cli)")]
        return

def wait(t):
    for remaining in range(t, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining...".format(remaining))
        sys.stdout.flush()
        time.sleep(1)

    sys.stdout.write("\rcontinue working            \n")

def alternate(c):
    time.sleep(3)
    credentials = Account('admin', 'password')
    c = SSH2()
    c.set_driver(OLTClishDriver())
    c.connect(ipaddr)
    c.login(credentials)
    time.sleep(5)
    print "connection established"
    c.send("firmware select image-alternate\r")
    c.expect("(y/N)")
    time.sleep(5)
    c.send("y\r")
    c.expect("(y/N)")
    time.sleep(5)
    c.send("y\r")
    c.expect("#")
    c.execute("show firmware")
    print c.response
    time.sleep(5)
    c.send("reboot system\r")
    print "***********rebooting system***********"
    time.sleep(5)
    c.send("y\r")
    print "now wait for 500sec to connect MA for confirming of firmware-image"
    wait(500)
    print "connecting..."
    credentials = Account('admin', 'password')
    c = SSH2()
    c.set_driver(OLTClishDriver())
    c.connect(ipaddr)
    c.login(credentials)
    time.sleep(5)
    print "connection established"
    c.execute("firmware confirm")
    print "firmware confirmed. End loading..."
    wait(300)

def checker(vers,c):
    res_vers = vers
    vercount = 0
    ipaddr = namespace.ipaddr
    credentials = Account('admin', 'password')
    con = SSH2()
    con.set_driver(OLTClishDriver())
    c.connect(ipaddr)
    c.login(credentials)
    time.sleep(5)
    print "connection established"
    c.execute("show firmware")
    ver = c.response
    print "testing version", res_vers
    for line in ver.splitlines():
        if "{version}".format(version = vers) in line:
            if line.strip().split()[3] == "*":
                vercount += 1
                print line
    if vercount == 0:
        alternate(c)

        checker(res_vers, c)
    if vercount == 1:
        time.sleep(3)
        c.send("firmware select image-alternate untit 1\r")
        c.expect("(y/N)")
        time.sleep(5)
        c.send("y\r")
        c.expect("(y/N)")
        time.sleep(5)
        c.send("y\r")
        c.expect("#")
        c.execute("show firmware")
        print c.response
        time.sleep(5)
        c.send("reboot system\r")
        print "***********rebooting system***********"
        time.sleep(5)
        c.send("y\r")
        print "now wait for 500sec to connect MA for confirming of firmware-image"
        wait(500)
        print "connecting..."
        credentials = Account('admin', 'password')
        c = SSH2()
        c.set_driver(OLTClishDriver())
        c.connect(ipaddr)
        c.login(credentials)
        time.sleep(5)
        print "connection established"
        c.execute("firmware confirm")
        print "Firmware confirmed. End loading..."
        wait(300)
        checker(res_vers, c)
    if vercount == 2:
        print "Firmware successfully checked. Starting loojing for 11 vlan version {testvers}\n\n".format(testvers = res_vers)


def checkvlan(c):
    ipaddr = namespace.ipaddr
    credentials = Account('admin', 'password')
    con = SSH2()
    con.set_driver(OLTClishDriver())
    c.connect(ipaddr)
    count = 0
    pon_port = 0
    slot_chan = 0
    plc_slot_chan = 0
    vers = "3 26 2 41 48154"
    checker(vers, c)
    c.execute("show vlan 11")
    vlans = c.response
    print vlans
    for line in vlans.splitlines():
        if "plc-pon-port" in line:
            pon_port += 1
        if "plc-slot-channel" in line:
            plc_slot_chan += 1
        if "slot-channel" in line:
            slot_chan += 1
    if (pon_port == 128) and (plc_slot_chan == 16) and (slot_chan == 33):
        print "all ports tagged 11 vlan"
        c.send("copy tftp://192.168.16.16/vlan11_check_config fs://backup\r")
        wait(90)
        c.execute("commit")
        wait(200)
        c.execute("confirm")
        wait(20)
        print "configuration confirmed"
    else:
        print "WE_HAVE_PROBLEMS_SHUTDOWN_SCRIPT!!!"
        print slot_chan
        print plc_slot_chan
        print pon_port
        with open("11Vlan_test.log", "a") as logfile:
            logfile.write(vlans)
        c.execute("copy fs://log/pp tftp://192.168.16.16/11vlan_lose")
        c.execute("exit")
        #     #logfile.write(conf)
        #     logfile.write('\r\n\++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\r\n')

    with open("11Vlan_test.log", "a") as logfile:
        logfile.write("all 11 vlans in configuration\n\n")
    alternate(c)
    alternate(c)
    #c.expect("#")
    #print "#"
        #         print line
                        #     for line in vlans.splitlines():
                        #       print line
                        # print vid

if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    for iteration in xrange(1, 10000):
        print "\n"
        print "iteration", iteration, "\n"
        with open("11Vlan_test.log", "a") as logfile:
            logfile.write("********** iteration # {} **********\n\n".format(iteration))
        ipaddr = namespace.ipaddr
        credentials = Account('admin', 'password')
        con = SSH2()
        con.set_driver(OLTClishDriver())
        con.connect(ipaddr)
        con.login(credentials)

        try:
            checkvlan(con)
        except KeyboardInterrupt:
            exit()

