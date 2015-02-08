#!/usr/bin/python3.4
import requests, getpass, sys, time
from requests.auth import HTTPBasicAuth
from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor


#db connection vars
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

#found host computer - print server version
print("\ncouchDB host found - version " + r.json().get('version'))

#put and remove a new database to determine admin rights
r = requests.put(dbHost + 'admin_rights_verify_db', auth=dbAuth)
r = requests.delete(dbHost + 'admin_rights_verify_db', auth=dbAuth)
if r.json().get('error') == 'unauthorized':
    print('Connection failed: unauthorized credentials.')
    sys.exit()

#get json document containing all gun variations
weapons_list = requests.get(dbHost + 'tracked_steam_item_names/weapons_list', auth=dbAuth)
#print(str(r.json()).encode('utf-8').strip())


#for each market item in the document, build a string a retrieve the appropriate data

while True:
    db_document_data = {'month_day':None, 'week_day':None, 'time':None, 'tracked_items':{}}

    db_document_data['month_day'] = time.localtime().tm_mday
    db_document_data['week_day'] = time.localtime().tm_wday
    db_document_data['time'] = str(time.localtime().tm_hour) + ':' + str(time.localtime().tm_min) + ':' + str(time.localtime().tm_sec)

    print(db_document_data)

    #fill out initial data
    attempted_requests = 0
    successful_requests = 0

    session = FuturesSession(executor=ThreadPoolExecutor(max_workers=10))
    for weapon_base_name in weapons_list.json().get('weapons'):
        print('Now finding: ' + weapon_base_name.get('name'))
        #each item in requests_list[] is an array consisting of [request object, string item name]
        requests_list = []
        for weapon_skin_name in weapon_base_name.get('skins'):
            for weapon_condition in weapon_skin_name.get('conditions'):
                if not weapon_condition is None:
                    fully_qualified_weapon_name = weapon_base_name.get('name') + ' | ' + weapon_skin_name.get('name') + ' (' + weapon_condition + ')'
                    weapon_data_url = 'http://steamcommunity.com/market/priceoverview/?country=US&currency=1&appid=730&market_hash_name=' + fully_qualified_weapon_name
                    #add one item to the requests list consisting of [request object for later reference, market name]
                    time.sleep(0.1)
                    requests_list.append([session.get(weapon_data_url), fully_qualified_weapon_name])
                    attempted_requests+=1

        #starting at the beginning of the list
        for request in requests_list:
            if 'Access Denied' in str(request[0].result().content):
                print(request[1] + ': access denied.')
            elif request[0].result().json().get('lowest_price') is None:
                print(request[1] + ': weapon not on market.')
                successful_requests+=1
            else:
                lowest_price = request[0].result().json.get('lowest_price').replace('&#36;', '$')
                    print(request[1] + ': ' + lowest_price)
                    db_document_data['tracked_items'][request[1]] = lowest_price
                    successful_requests+=1
    #print(db_document_data)
    print('Successful requests this round: ' + str(successful_requests) + '/' + str(attempted_requests))
