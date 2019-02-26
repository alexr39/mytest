import sys
import pexpect
import Exscript
import re
import commands

def checker(vers,c):
    res_vers = vers
    vercount = 0
    c.execute("show firmware")
    ver = c.response
    for line in ver.slpitlines():
        if "{version}".format(version = vers) in line:
            if line.stip().split()[3] == "*":
                vercount += 1
                print line
    if vercount == 0:
        time.sleep(3)
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
        # c.expect("Do you really want to reload system ? (y/n)")
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
        # c.expect("Do you really want to reload system ? (y/n)")
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
        print "Firmware successfully checked. Starting test on version {testvers}".format(testvers = res_vers)

