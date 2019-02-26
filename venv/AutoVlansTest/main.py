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
        print "Firmware successfully checked. Starting test on version {testvers}\n\n".format(testvers = res_vers)


def checkvlan(c):
    count = 0
#    c.execute("show running-config template all")
#    for line in c.response.splitlines():
#        if "name" in line:
#           tempname = line.strip().split()[-1]
#            print tempname
#     c.execute("show vlan 3505")
#     cc_3505 = c.response
#     c.execute("show vlan 3547")
#     cc_3547 = c.response
#     c.execute("show vlan 3527")
#     cc_3527 = c.response
#     c.execute("show running-config interface ont 0-15/0-7/0-63")
#     run = c.response
    # for line in run.splitlines():
    #     if line.strip().startswith("interface ont 0/0/0"):
    #         print line
#    c.execute("show running-config interface ont 0-15/0-7/0-63")
#    run = c.response
    vers = "3 26 2 24 47970"
    checker(vers, c)
    for slot in xrange(0 , 16):
        for port in xrange(0,8):
            for ont in xrange(0,64):
                print "ont {slot}/{port}/{ont}".format(slot = slot, port = port, ont = ont)

                c.execute("show running-config interface ont {slot}/{port}/{ont}".format(slot = slot, port = port, ont = ont))
                conf = c.response
               # print conf
                # for line in run.splitlines():
                #     if line.strip().startswith("interface ont {slot}/{port}/{ont}".format(slot = slot, port = port, ont = ont)):
                #         if "template" in line.strip()
                #         print line
 #                #print cc_3505
 #                #print cc_3547
 #                #print cc_3527
                for line in conf.splitlines():
 #                    if "template-01" in line:
 #                        ccvlans = [3505, 3547, 3527]
 #                       # for cc in ccvlans:
 # #                           c.execute("show vlan {}".format(cc))
 # #                           vlans = c.response
 #                        if "plc-pon-port {slot}/{port}".format(slot = slot, port = port) in cc_3505:
 #                            print "plc-pon-port {slot}/{port} tagged with service vlan {vl} ONT {on}".format(slot = slot, port = port, vl = 3505, on = ont)
 #                        else:
 #                            print "service vlan {} problem".format(3505)
 #                        if "plc-pon-port {slot}/{port}".format(slot = slot, port = port) in cc_3547:
 #                            print "plc-pon-port {slot}/{port} tagged with service vlan {vl} ONT {on}".format(slot = slot, port = port, vl = 3547, on = ont)
 #                        else:
 #                            print "service vlan {} problem".format(3547)
 #                        if "plc-pon-port {slot}/{port}".format(slot = slot, port = port) in cc_3527:
 #                            print "plc-pon-port {slot}/{port} tagged with service vlan {vl} ONT {on}".format(slot = slot, port = port, vl = 3527, on = ont)
 #                        else:
 #                            print "service vlan {} problem".format(3527)
                    if "custom cvid" in line:
                        count = count+1
                        print "ont {slot}/{port}/{ont}".format(slot=slot, port=port, ont=ont)
                        print line
                        vid = line.strip().split()[-1]
                        c.execute("show vlan {}".format(vid))
                        vlans = c.response
                        #for line in vlans.splitlines():
                        if "plc-pon-port {slot}/{port}".format(slot = slot, port = port) in vlans:
                            print "plc-pon-port {slot}/{port} tagged".format(slot = slot, port = port)
                          #  print vlans
                        else:
                            print "WE_HAVE_PROBLEMS_SHUTDOWN_SCRIPT!!!"
                            with open("noVlan_test.log", "a") as logfile:
                                logfile.write("not found auto configured custom vlan {vl} from ont {slot}/{port}/{ont}\n".format(vl=vid, slot = slot, port = port, ont = ont))
                            c.execute("copy fs://log/slot{slot} tftp://192.168.16.16/vlansdropslot{slot}".format(slot = slot) )
                            c.execute("exit")
                           #     #logfile.write(conf)
                           #     logfile.write('\r\n\++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\r\n')
    with open("noVlan_test.log", "a") as logfile:
        logfile.write("all custom vlans in configuration {}\n\n".format(count))
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
        with open("noVlan_test.log", "a") as logfile:
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

