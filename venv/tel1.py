import re
import commands
import time
from Exscript import Account
from Exscript.protocols import SSH2
from Exscript.protocols.drivers.driver import Driver
from Exscript.protocols.Exception import InvalidCommandException


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


_linux_user_re = [re.compile(r"login: ")]
_linux_password_re = [re.compile(r"password:", re.I)]
_all_prompt_re = [re.compile(r"\r?\n?\[root@\S*\s/root\]\$"),
                    r"OLT CLI>",
                    r"OLT CLI#",
                    re.compile(r"OLT CLI(\S+\s?\S*)#")]



class OLTLinuxDriver(Driver):
    def __init__(self):
        Driver.__init__(self, "OLTLinuxDriver")
        self.user_re = _linux_user_re
        self.password_re = _linux_password_re
        self.prompt_re = _all_prompt_re


IP_LTP = '192.168.199.147'
accl = Account('admin', 'password')
conl = SSH2(timeout=60)
#conl.set_driver(OLTLinuxDriver())
conl.connect(IP_LTP)
conl.login(accl)

for iteration in xrange(0,10000):
        print ('\r\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\r\n')
        print '************************ reconfiguration cycle', iteration, '************************'
        with open('reconfiguration_log.log', 'a') as logfile:
            logfile.write('************************ reconfiguration cycle {iter} ************************\r\n'.format(iter=iteration))
        time_LTP=''

        time.sleep(3)
        conl.execute('reconfigure interface gpon-port 0-3')
        answer = conl.response
        with open('reconfiguration_log.log', 'a') as logfile:
            logfile.write(answer)

        for res in xrange(0,39):
            time.sleep(30)
            conl.execute('show resources pmchal')
            resources = conl.response
            with open('reconfiguration_log.log', 'a') as logfile:
                logfile.write(resources)
                logfile.write('\r\n****************************************************************************************************************\r\n')


        for i in xrange(0,3):
            time.sleep(30)
        with open('reconfiguration_log.log', 'a') as logfile:
            logfile.write('starting new reconfiguration cycle\r\n')

cona.close()