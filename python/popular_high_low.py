#!/usr/bin/python3.4

import requests, json, time, urllib

popular_items_url = 'http://steamcommunity.com/market/popular?country=US&language=english&currency=1&count=100'

r = requests.get(popular_items_url)
str_content = str(r.content)
if ',"results_html' in str_content:
	print('contains results.html')
else:
	print ('not found')

str_json = str_content.partition(',"results_html')[0].partition('"data":')[2]

fixed_string = str_json.replace("\\'", "'")
json_object = json.loads(fixed_string)

steam_item_prefix_url = 'http://steamcommunity.com/market/listings/730/'

for steam_item in json_object:
	if '|' in steam_item.get('name'): #filters all non-counterstrike items
		time.sleep(1)

		item_url_unicode = steam_item.get('name').replace("'", "\\'")
		request_url_unicode = steam_item_prefix_url + item_url_unicode

		
		r = requests.get(str((request_url_unicode).format('c')))
		if not 'line1=' in str(r.content):
			print(request_url_unicode)
