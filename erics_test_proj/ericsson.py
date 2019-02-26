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
    def __init__(self, sn , oid):
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
        con.execute('exit')
        #con.execute('commit')
        #con.execute('confirm')
        print ('added successfully')

    def checkok(self):
        #wait(20)
        con.execute('show interface ont 5 online ok')
        self.resp = con.response
        #print self.resp
        for line in self.resp.splitlines():
            if self.sn in line:
                print ('ONT with serial {} and id {} in OK state'.format(self.sn, self.oid))
            else:
                continue

    def delont(self):
        #delete ONT from config
        con.execute('configure terminal')
        con.execute('no interface ont {}'.format(self.oid))
        con.execute('exit')
        #con.execute('commit')
        #con.execute('confirm')
        print ('ONT delete successfully')

    def triplplay(self):
        con.execute('interface ont {}'.format(self.oid))
        con.execute('service 0 profile cross-connect IMS-ERCS dba dba-00')
        con.execute('service 1 profile cross-connect HSI-ERCS dba dba-00')
        con.execute('profile voice "voice"')
        con.execute('voice port 0 number "420013"')
        con.execute('voice port 0 authentication username "420013"')
        con.execute('voice port 0 authentication password "420013"')
        con.execute('exit')
        con.execute('do commit')
        con.execute('do confirm')
        print ('3play on ont {} configured successfully'.format(self.oid))

    def commitconfirm(self):
        con.execute('commit')
        con.execute('confirm')
        wait(20)

    def onevoice(self, num):
        con.execute('configure terminal')
        con.execute('interface ont {}'.format(self.oid))
        con.execute('service 7 profile cross-connect IMS-ERCS dba dba-00')
        con.execute('voice port 0 number {}'.format(str(num)))
        con.execute('voice port 0 authentication username {}'.format(str(num)))
        con.execute('voice port 0 authentication password {}'.format(str(num)))
        con.execute('exit')
        con.execute('exit')


if __name__ == '__main__':
    ont_list = []
    # list ONT serials to create objects
    serial_list = [('5/0/10', 'ELTX66002238'), ('5/0/11', 'ELTX6E009E44')]
    parser = createParser()
    argum = parser.parse_args(sys.argv[1:])
    ipaddr = argum.ipaddr
    credentials = Account('admin', 'password')
    con = SSH2()
    con.set_driver(OLTClishDriver())
    con.connect(ipaddr)
    con.login(credentials)
    while True:
        job = raw_input('What do you want to do: ')
        if job == 'delete':
            for ont in ont_list:
                ont.delont()
            ont.commitconfirm()
        elif job == 'onevoice':
            num = 4001
            for ont in ont_list:
                ont.onevoice(num)
                num += 1
            ont.commitconfirm()
        elif job == 'create':
            for sn, oid in serial_list:
                ont = Ont(oid, sn)
                ont.configont()
                ont_list.append(ont)
                print(ont)
            ont.commitconfirm()
        elif job == 'check':
            for ont in ont_list:
                ont.checkok()
        elif job == 'exit':
            break


