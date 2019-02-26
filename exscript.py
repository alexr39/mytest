from Exscript.util.interact import read_login
from Exscript.protocols import SSH2

account = read_login()    # Prompt the user for his name and password
conn = SSH2()             # We choose to use SSH2
conn.connect('localhost') # Open the SSH connection
conn.login(account)       # Authenticate on the remote host
conn.execute('uname -a')  # Execute the "uname -a" command
conn.send('exit\r')       # Send the "exit" command
conn.close()              # Wait for the connection to close
