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

def reconfig():
    con.execute("reconfigure interface ont 2/0-30,50-60,100-114")
    print("reconfigure ONT")

def checkstate():
    print("waiting for OK state")
    wait(170)
    con.execute("show interface ont 2 online")
    state = con.response
    print state
    for line in state.splitlines():
        if "Total" in line:
            if "126" in line:
                print("everything is OK, reconfiguring")
                return "OK"
            else:
                print("lose OK ONT")
                return "stop"


if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    ipaddr = namespace.ipaddr
    credentials = Account('admin', 'password')
    con = SSH2()
    con.set_driver(OLTClishDriver())
    con.connect(ipaddr)
    con.login(credentials)
    for iteration in xrange(1, 10000):
        print "\n"
        print "iteration", iteration, "\n"
        reconfig()
        checkstate()
        if checkstate()=="stop":
            break


