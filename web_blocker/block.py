
import time
from datetime import datetime as dt




# Path to hosts  file, redirect, websites to block
host_path = 'hosts'
redirect = '127.0.0.1'
website_list = ['www.facebook.com']


while True:
    if dt(dt.now().year, dt.now().month, dt.now().day, 8)< dt.now() < dt(dt.now().year, dt.now().month, dt.now().day, 18):
        print ('Rihanna')
        file = open(host_path, 'r+')
        content = file.read()
        for website in website_list:
            if website in content:
                pass
            else:
                file.write(redirect + ' ' + website + '\n')
    else:
        print ('Drake')
    time.sleep(5)

