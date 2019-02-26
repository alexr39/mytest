#!/usr/bin/python2.7
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
    p.add_argument('-i', '--ipaddr', default='192.168.10.110')
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

def alternate():
    time.sleep(3)
    ipaddr = namespace.ipaddr
    credentials = Account('admin', 'password')
    c = SSH2()
    c.set_driver(OLTClishDriver())
    c.connect(ipaddr)
    c.login(credentials)
    time.sleep(5)
    print "connection established"
    c.send("copy tftp://192.168.10.30/ltp-8x-revc-3.36.0.611.fw.bin fs://firmware\r")
    time.sleep(5)
    c.expect("#")
    c.execute("show version\r")
    print c.response
    time.sleep(5)
    c.send("reboot\r")
    c.expect("(y/n)")
    c.send("y\r")
    print "***********rebooting system***********"
    print "now wait for 240 sec to connect MA for confirming of firmware-image"
    wait(240)
    print "connecting..."


if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    for iteration in xrange(1, 10000):
        print "\n"
        print "*************************iteration", iteration, "\n"
        try:
            print "----------------------------------update----------------------------------"
            alternate()
        except KeyboardInterrupt:
            exit()

