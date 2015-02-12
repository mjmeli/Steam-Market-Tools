#!/usr/bin/python3.4

import requests, json, time, sys, getpass
from requests.auth import HTTPBasicAuth
from statistics import mean, stdev
from datetime import datetime, timedelta
from time import mktime
from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup as bs

#User Settings
using_couchdb_data = False
include_graph = True
historic_length_days = 30
request_spacing = 1 #seconds
output_html = False
dbHost = 'http://104.236.192.200:5984/'

#Vars
steam_item_prefix_url = 'http://steamcommunity.com/market/listings/730/'
steam_item_db = []
requests_made = 0
requests_to_make = 0
requests_successful = 0
requests_failed = 0
dbAuth = None


#--------------------------------FUNCTIONS--------------------------------------

def reject_outliers(data, m=2):	
	data_mean = mean(data)
	data_stdev = stdev(data)
	good_data = []

	for data_point in data:
		#if the distance from the mean is > 2x the stdev, remove the data
		if(abs(data_point - data_mean) < (m * data_stdev)):
			good_data.append(data_point)
	return good_data

def get_buy_and_sell_price(data, m=2):	
	data_mean = mean(data)
	data_stdev = stdev(data)
	good_data = []

	for data_point in data:
		#if the distance from the mean is > 2x the stdev, remove the data
		if(abs(data_point - data_mean) < (m * data_stdev)):
			good_data.append(data_point)
	return good_data

#Retrieve weapons list from pre-compiled  list in couchdb
def get_weapons_from_couchdb():
	#db connection vars
	global dbAuth
	global dbHost
	dbUser = input("db username: ")
	dbPass = getpass.getpass("password: ")
	dbAuth = HTTPBasicAuth(dbUser, dbPass)
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
	weapons_list_flat = []
	for weapon_base_name in weapons_list.json().get('weapons'):
		for weapon_skin_name in weapon_base_name.get('skins'):
			for weapon_condition in weapon_skin_name.get('conditions'):
				if not weapon_condition is None:
					fully_qualified_weapon_name = weapon_base_name.get('name') + ' | ' + weapon_skin_name.get('name') + ' (' + weapon_condition + ')'
					weapons_list_flat.append(fully_qualified_weapon_name)

	return weapons_list_flat

#Retrieve weapons list from the 'Popular' page at the front of the marketplace
def get_weapons_from_popular():
	popular_items_url = 'http://steamcommunity.com/market/popular?country=US&language=english&currency=1&count=100'
	r = requests.get(popular_items_url)
	str_content = str(r.content)
	if ',"results_html' in str_content:
		print('Retrieved list of popularly traded items.')
	else:
		print ('not found')
	str_json = str_content.partition(',"results_html')[0].partition('"data":')[2]
	fixed_string = str_json.replace("\\'", "'")
	weapons_list = []
	json_object = json.loads(fixed_string)
	for steam_item in json_object:
		if '|' in steam_item.get('name'): #filters all non-counterstrike items
			weapons_list.append(steam_item.get('name').replace("'", "\\'"))
	return weapons_list

#Draws a progress indicator featuring retrieved/total and faulty responses
def draw_progress(num_made, num_failed, num_required):
	global request_spacing
	
	num_remaining = num_required - num_made
	sec = timedelta(seconds=(request_spacing * num_remaining))
	d = datetime(1,1,1) + sec
	sys.stdout.write("\rRetrieved: " + str(num_made) + '/' + str(num_required) +  ' | Faulty: ' + str(num_failed) + ' | Time remaining: ' + str(d.minute) + ':' + str(d.second) + '    ')
	sys.stdout.flush()

#Process a pre-defined number of future-requests, or iterate to the end of the list
def process_x_futures(x, requests_list):
	global requests_made
	global requests_to_make
	global requests_successful
	global requests_failed

	futures_processed = 0
	if(len(requests_list) == 0):
		return
	for request in requests_list:
		if futures_processed == x:
			break
		if request[3] is False: #not yet processed
			try:
				str_content = str(request[0].result().content)

				json_decode_success = False

				#if using popular data
				str_item_json = str_content.partition('line1=')[2].partition(']];')[0] + ']]'
				try:
					item_json = json.loads(str_item_json)
					json_decode_success = True
				except Exception as detail:
					#if using db data
					requests_failed += 1
					futures_processed += 1
					request[3] = True #request has been processed
					draw_progress(requests_made, requests_failed, requests_to_make)

				item_prices = []
				item_sale_volume = []
				graph_points = {}

				if json_decode_success:
					
					for steam_sale in item_json:
						#pull sale data from 7 days ago and less
						stripped_time = time.strptime(steam_sale[0].partition(':')[0] ,'%b %d %Y %H')
						dt = datetime.fromtimestamp(mktime(stripped_time))
						t_delta = (datetime.now() - dt)
						if(t_delta.days <= historic_length_days):
							item_prices.append(steam_sale[1])
							item_sale_volume.append(steam_sale[2])
							graph_points[str(dt)] = steam_sale[1]

					#discard some outliers who lie more than 2 stdevs outside of mean
					if(len(item_prices) >= 2):
						cleaned_data = reject_outliers(item_prices)
						if(len(cleaned_data) > 0):
							min_price = round(min(cleaned_data),2)
							max_price = round(max(cleaned_data),2)
							mean_price = round(mean(cleaned_data), 2)


							mean_sale_volume = round(mean([int(i) for i in item_sale_volume]), 0)

							#calculate fees, assuming you will be buying at the lowest and selling at the highest price
							fees = round(min_price * 0.15, 2)
							profit = round(max_price - min_price - fees, 2)
							percent_gains = round(((profit / min_price) * 100),2)

							if mean_sale_volume > 5:
								if include_graph is True:
									steam_item_db.append([request[1], mean_price, profit, percent_gains, mean_sale_volume, request[2], graph_points])
								else: 
									steam_item_db.append([request[1], mean_price, profit, percent_gains, mean_sale_volume, request[2]])
							requests_successful += 1
						else:
							requests_failed += 1
					else:
						requests_failed += 1
					futures_processed += 1
				request[3] = True
			except:
				requests_failed += 1
			draw_progress(requests_made, requests_failed, requests_to_make)

#--------------------------------END OF FUNCTIONS----------------------------------


#----------------------------------MAIN METHOD-------------------------------------
if using_couchdb_data:
	steam_item_list = get_weapons_from_couchdb()
else:
	steam_item_list = get_weapons_from_popular()

requests_to_make = len(steam_item_list)

if(requests_to_make) is 0:
	print('No steam items found for lookup.')
	sys.exit()

#async portion
session = FuturesSession(executor=ThreadPoolExecutor(max_workers=5))
requests_list = []

current_count = 0
read_responses_after = 10

for steam_item in steam_item_list:
	request_url = steam_item_prefix_url + steam_item
	requests_list.append([session.get(request_url, stream=False), steam_item, request_url, False])
	time.sleep(request_spacing) #sleep request_spacing seconds to avoid anti-DDOS mechanisms
	requests_made += 1
	current_count += 1
	#to preserve RAM, we will not keep all page-responses in memory.
	if current_count >= read_responses_after:
		current_count = 0
		process_x_futures(read_responses_after, requests_list)
	draw_progress(requests_made, requests_failed, requests_to_make)

#Function get_key is required to allow for custom sort (descending)
def get_key(item):
	return item[2]

sorted_steam_item_db = sorted(steam_item_db, key=get_key, reverse=True)

#---------------------------BEGIN  DB  OUTPUT SEGMENT------------------------------
uuid = str(datetime.now())

db_document = {}
db_items_list = []

for db_item in sorted_steam_item_db:
	#db_document['tracked_items'].
	if include_graph:
		item_properties = {'name':db_item[0], 'price': db_item[1], 'profit': db_item[2], 'gains_percent':db_item[3], 'mean_sale_volume': db_item[4], 'graph_points': db_item[6]}
	else:
		item_properties = {'name':db_item[0], 'price': db_item[1], 'profit': db_item[2], 'gains_percent':db_item[3], 'mean_sale_volume': db_item[4]}

	db_items_list.append(item_properties)

db_document['steam_items'] = db_items_list
#things to go in DB: ('price':steam_item[1]) ('profit':steam_item[2])
#('gain_percent':steam_item[3]) ('mean_sale_volume':)

print('Uploading data to database...')
r = requests.put(dbHost + 'tracked_steam_item_stats' + '/' + uuid, auth=dbAuth, data=json.dumps(db_document))
print(r.json())
#----------------------------END  DB  OUTPUT SEGMENT-------------------------------


#---------------------------BEGIN HTML OUTPUT SEGMENT------------------------------
print('\nResults: ')

html_to_print = ''
html_to_print += '<!DOCTYPE html>'
html_to_print +='<html>'
html_to_print +='<head>'
html_to_print +='<title>Steam Market Stats</title>'
html_to_print +='<link rel="stylesheet" type="text/css" href="styles.css">'

html_to_print +='<script src="https://code.jquery.com/jquery-2.1.3.min.js"></script>'
html_to_print +='<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/css/bootstrap.min.css">'
html_to_print +='<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/css/bootstrap-theme.min.css">'
html_to_print +='<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/js/bootstrap.min.js"></script>'
html_to_print +='</head>'
html_to_print +='<body>'
html_to_print +='<div class="container"><div class="starter-template"><h1>' + 'Most Profitable CS:GO Items - ' + str(datetime.now()) + '</h1><p class="lead">Based on the top 100 active items</p>'

for steam_item in sorted_steam_item_db:
	#print(steam_item[0] + '\n - Price: $' + str(steam_item[1]) + '\n - Profit: ' + str(steam_item[2]) + '\n - Gain: ' + str(steam_item[3]) + '%\n - Average sale volume: ' + str(round(steam_item[4],0)) + '\n')
	html_to_print += '<p>'
	html_to_print += '<a href="' + steam_item[5] +'">'+ steam_item[0] + '</a>'
	html_to_print += '<ul>' + 'Price: $' + str(steam_item[1]) + '</ul>'
	html_to_print += '<ul>' + 'Profit: $' + str(steam_item[2]) + '</ul>'
	html_to_print += '<ul>' + 'Gain: ' + str(steam_item[3]) + '&#37;</ul>'
	html_to_print += '<ul>' + 'Average sale volume: ' + str(round(steam_item[4],0)) + '</ul>'
	html_to_print += '</p>'

html_to_print += '</div>'
html_to_print += '</body>'
html_to_print += '</html>'

my_soup = bs(html_to_print).prettify()

if(output_html):
	outfile = open('async_output.html', 'w')
	outfile.write(my_soup)
#---------------------------END HTML OUTPUT SEGMENT---------------------------------