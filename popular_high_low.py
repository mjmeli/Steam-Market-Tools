#!/usr/bin/python3.4

import requests, json, re, html



popular_items_url = 'http://steamcommunity.com/market/popular?country=US&language=english&currency=1&count=100'

r = requests.get(popular_items_url)
str_content = str(r.content)
if ',"results_html' in str_content:
	print('contains results.html')
else:
	print ('not found')

str_json = str_content.partition(',"results_html')[0].partition('"data":')[2]
f = open('json_popular.txt', 'w')
f.write(str_json)

#print(str_json)

good_json = print(html.unescape(str_json))
#print(regexed_popular)



#popular_json = json.loads(good_json)

#cleaned_str_json = str_json.replace

#json_str_content = json.loads(str_json)

#print (json_str_content)


