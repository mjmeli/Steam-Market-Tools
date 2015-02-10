#!/usr/bin/python3.4

import requests, json, time, sys
from statistics import mean, stdev
from datetime import datetime
from time import mktime

def reject_outliers(data, m=2):	
	data_mean = mean(data)
	data_stdev = stdev(data)
	good_data = []

	for data_point in data:
		#if the distance from the mean is > 2x the stdev, remove the data
		if(abs(data_point - data_mean) < (m * data_stdev)):
			good_data.append(data_point)
	return good_data

popular_items_url = 'http://steamcommunity.com/market/popular?country=US&language=english&currency=1&count=100'

r = requests.get(popular_items_url)
str_content = str(r.content)
if ',"results_html' in str_content:
	print('Retrieved most popular file list.')
else:
	print ('not found')

str_json = str_content.partition(',"results_html')[0].partition('"data":')[2]

fixed_string = str_json.replace("\\'", "'")
json_object = json.loads(fixed_string)

steam_item_prefix_url = 'http://steamcommunity.com/market/listings/730/'

steam_item_db = []

successful_requests = 0
json_failures = 0

for steam_item in json_object:
	if '|' in steam_item.get('name'): #filters all non-counterstrike items
		
		request_url = steam_item_prefix_url + steam_item.get('name').replace("'", "\\'")
		request_url_unicode = request_url.encode().decode()
		r = requests.get(request_url_unicode)
		time.sleep(.5) #sleep .5 seconds to avert any problems that might arise from trying to request too quickly
		str_content = str(r.content)

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

			steam_item_db.append([steam_item.get('name'), mean_price, profit, percent_gains, mean_sale_volume])
			successful_requests += 1
			sys.stdout.write("\rRetrieved: " + str(successful_requests) + ' | JSON failures: ' + str(json_failures))
			sys.stdout.flush()

#finally, create a single-line-item list sorted by greatest profit
def getKey(item):
	return item[2]

sorted_steam_item_db = sorted(steam_item_db, key=getKey, reverse=True)

print('\nResults: ')

for steam_item in sorted_steam_item_db:
	print(steam_item[0] + '\n - Price: ' + str(steam_item[1]) + '\n - Profit: ' + str(steam_item[2]) + '\n - Gains: ' + str(steam_item[3]) + '\n - Average sale volume: ' + str(steam_item[4]) + '%\n')


