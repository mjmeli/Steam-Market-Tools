#!/usr/bin/python3.4

import requests, json, time, sys
from statistics import mean, stdev
from datetime import datetime
from time import mktime
from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup as bs

def reject_outliers(data, m=2):	
	data_mean = mean(data)
	data_stdev = stdev(data)
	good_data = []

	for data_point in data:
		#if the distance from the mean is > 2x the stdev, remove the data
		if(abs(data_point - data_mean) < (m * data_stdev)):
			good_data.append(data_point)
	return good_data

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

popular_items_url = 'http://steamcommunity.com/market/popular?country=US&language=english&currency=1&count=100'

r = requests.get(popular_items_url)
str_content = str(r.content)
if ',"results_html' in str_content:
	print('Retrieved list of popularly traded items.')
else:
	print ('not found')

str_json = str_content.partition(',"results_html')[0].partition('"data":')[2]

fixed_string = str_json.replace("\\'", "'")
json_object = json.loads(fixed_string)

steam_item_prefix_url = 'http://steamcommunity.com/market/listings/730/'

steam_item_db = []

requests_made = 0
successful_requests = 0
json_failures = 0

#async portion
session = FuturesSession(executor=ThreadPoolExecutor(max_workers=5))
requests_list = []

requests_to_make = 0
spinner = spinning_cursor()

for steam_item in json_object:
	if '|' in steam_item.get('name'): #filters all non-counterstrike items
		requests_to_make += 1


for steam_item in json_object:
	if '|' in steam_item.get('name'): #filters all non-counterstrike items

		request_url = steam_item_prefix_url + steam_item.get('name').replace("'", "\\'")
		request_url_unicode = request_url.encode().decode()
		requests_list.append([session.get(request_url_unicode, stream=False), steam_item.get('name'), request_url_unicode])
		time.sleep(1) #sleep .5 seconds to avert any problems that might arise from trying to request too quickly
		requests_made += 1
		sys.stdout.write("\r%d%%" % (100 * (requests_made / requests_to_make)))
		sys.stdout.flush()

#next section is part of the next iteration
for request in requests_list:
	str_content = str(request[0].result().content)

	str_item_json = str_content.partition('line1=')[2].partition(']];')[0] + ']]'

	json_decode_success = False
	try:
		item_json = json.loads(str_item_json)
		json_decode_success = True
	except Exception as detail:
		#print(detail)
		json_failures += 1
		sys.stdout.write("\rRetrieved: " + str(successful_requests) + ' | JSON failures: ' + str(json_failures))
		sys.stdout.flush()

	if json_decode_success:
		item_prices = []
		item_sale_volume = []
		for steam_sale in item_json:
			#pull sale data from 7 days ago and less
			stripped_time = time.strptime(steam_sale[0].partition(':')[0] ,'%b %d %Y %H')
			dt = datetime.fromtimestamp(mktime(stripped_time))
			t_delta = (datetime.now() - dt)
			if(t_delta.days <= 7):
				item_prices.append(steam_sale[1])
				item_sale_volume.append(steam_sale[2])

		#discard some outliers who lie more than 2 stdevs outside of mean
		cleaned_data = reject_outliers(item_prices)

		min_price = round(min(cleaned_data),2)
		max_price = round(max(cleaned_data),2)
		mean_price = round(mean(cleaned_data), 2)

		mean_sale_volume = round(mean(cleaned_data), 0)

		#calculate fees, assuming you will be buying at the lowest and selling at the highest price
		fees = round(min_price * 0.15, 2)
		profit = round(max_price - min_price - fees, 2)
		percent_gains = round(((profit / min_price) * 100),2)

		if mean_sale_volume > 5:
			steam_item_db.append([request[1], mean_price, profit, percent_gains, mean_sale_volume, request[2]])

		successful_requests += 1
		sys.stdout.write("\rRetrieved: " + str(successful_requests) + ' | Parsing failures: ' + str(json_failures))
		sys.stdout.flush()

#finally, create a single-line-item list sorted by greatest profit
def getKey(item):
	return item[2]

sorted_steam_item_db = sorted(steam_item_db, key=getKey, reverse=True)

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
	print(steam_item[0] + '\n - Price: $' + str(steam_item[1]) + '\n - Profit: ' + str(steam_item[2]) + '\n - Gain: ' + str(steam_item[3]) + '%\n - Average sale volume: ' + str(round(steam_item[4],0)) + '\n')
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

outfile = open('async_output.html', 'w')
outfile.write(my_soup)