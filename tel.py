import telnetlib

# constants
HOST = '192.168.199.147'
USER = b"admin"
PASSWORD = b"password"
# USER = raw_input("enter username")
#f = open("serial.txt", 'r')
#s = f.readlines()
#f.close()


tn = telnetlib.Telnet(HOST)
tn.read_until('login:')
tn.write(USER + b'\r')
tn.read_until(b"assword:")
tn.write(PASSWORD + b'\r')
tn.read_until(b"#")
tn.write("configure terminal\r")
tn.read_until(b")#")
tn.write("do show interface ont 3 unactivated\r")
print(tn.read_until(b')#')) #read all data from privious command to buff(tn.****) and print
tn.write("exit\r")
tn.read_until(b"#")
tn.write("exit\r")
tn.close()