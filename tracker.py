#!/usr/bin/python3.4
import requests, getpass, sys
from requests.auth import HTTPBasicAuth

#db connection
dbHost = 'http://steamtrack:5984/'
dbUser = input("db username: ")
dbPass = getpass.getpass("password: ")
dbAuth = HTTPBasicAuth(dbUser, dbPass)

#get server information - determine if hostname is correct
try:
   r = requests.get(dbHost)
except:
   #inappropriate/missing response from host
   print("\ncouchDB host not found: " + dbHost)
   sys.exit()

#found host computer
print("\ncouchDB host found - version " + r.json().get('version'))

#put and remove a new database to determine admin rights
r = requests.put(dbHost + 'admin_rights_verify_db', auth=dbAuth)
r = requests.delete(dbHost + 'admin_rights_verify_db', auth=dbAuth)
if r.json().get('error') == 'unauthorized':
   print('Connection failed: unauthorized credentials.')
   sys.exit()

#get json document containing all gun variations
r = requests.get(dbHost + 'tracked_steam_item_names/weapons_list', auth=dbAuth)
print(r.json())

#for each market item in the document, build a string
#http://steamcommunity.com/market/priceoverview/?country=US&currency=1&appid=730&market_hash_name=M4A1-S%20%7C%20Guardian%20%28Minimal%20Wear%29
#store the price data 
