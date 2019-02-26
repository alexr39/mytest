#! /usr/bin/python2.7
import argparse
import re
import commands
import time
import sys
import pexpect
import Exscript
from Exscript import Account
from Exscript.protocols import *
from Exscript.protocols.drivers.driver import Driver


def createParser():
    p = argparse.ArgumentParser()
    p.add_argument('-i', '--ipaddr', default='192.168.10.155')
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


class Ont:
    def __init__(self, oid, sn):
        self.sn = sn
        self.oid = oid
        print ('')

    def __str__(self):
        return 'ONT serial: {} \n ONT s/p/i: {}'.format(self.sn, self.oid)

    def configont(self):
        con.execute('configure terminal')
        con.execute('interface ont {}'.format(self.oid))
        con.execute('serial {}'.format(self.sn))
        con.execute('exit')
        con.execute('do commit')
        con.execute('do confirm')
        print ('added successfully')

    def checkok(self):
        wait(5)
        con.execute('do show interface ont 5 online ok')
        self.resp = con.response
        # print self.resp
        for line in self.resp.splitlines():
            if self.sn in line:
                print ('ONT with serial {} and id {} in OK state'.format(self.sn, self.oid))
            else:
                continue

    def delont(self):
        # delete ONT from config
        con.execute('no interface ont {}'.format(self.oid))
        con.execute('do commit')
        con.execute('do confirm')
        print ('ONT delete successfully')


if __name__ == '__main__':
    ex = False
    ont_list = []
    ont_dict = {'5/0/6':'ERSN001AEB10'} #dictionary for creating ONT ID:serial
    parser = createParser()
    argum = parser.parse_args(sys.argv[1:])
    ipaddr = argum.ipaddr
    credentials = Account('admin', 'password')
    con = SSH2()
    con.set_driver(OLTClishDriver())
    con.connect(ipaddr)
    con.login(credentials)
    while ex != True:
        # ont_serial = raw_input('Input serial ')
        # ont_id = raw_input('Input s/p/i ')
        # ont = Ont(ont_serial, ont_id)
        ont = Ont(ont_dict[0])
        ont.configont()
        ont.checkok()
        ont_list.append(ont)
        add = raw_input('Add another ONT? y/n ')
        if add == 'y':
            ex = False
            con.execute('exit')
        else:
            ex = True
            # print (ont_list)
            break
    delete = raw_input('Do you want to delete all ont? y/n: ')
    if delete == 'y':
        for ont in ont_list:
            ont.delont()

    # ont1 = Ont('ERSN001AEB10', '5/0/6')
    # ont1.configont()
    # ont1.checkok()
    # ont1.delont()
