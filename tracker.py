#!/usr/bin/python3.4
import requests, getpass, sys
from requests.auth import HTTPBasicAuth

dbHost = 'http://steamtrack:5984/'
dbUser = input("db username: ")
dbPass = getpass.getpass("password: ")

dbAuth = HTTPBasicAuth(dbUser, dbPass)
#get server information - determine if hostname is correct
try:
   r = requests.get(dbHost)
except:
   print("\ncouchDB host not found: " + dbHost)
   sys.exit()
   
#found host computer
print("\ncouchDB host found - version " + r.json().get('version'))

#put and remove new database to determine admin rights
r = requests.put(dbHost + 'admin_verify_db', auth=dbAuth)
r = requests.delete(dbHost + 'admin_verify_db', auth=dbAuth)
if r.json().get('error') == 'unauthorized':
   print('Connection failed: unauthorized credentials.')
   sys.exit()

