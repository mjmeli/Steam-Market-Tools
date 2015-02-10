#!/usr/bin/python3.4

import requests, json, time
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


#Start of main program

r = requests.get('http://steamcommunity.com/market/listings/730/M4A1-S%20%7C%20Cyrex%20(Minimal%20Wear)')
str_content = str(r.content)
str_item_json = str_content.partition('line1=')[2].partition(']];')[0] + ']]'
item_json = json.loads(str_item_json)

item_prices = []

for steam_item in item_json:
	#pull sale data from 7 days ago and less
	stripped_time = time.strptime(steam_item[0].partition(':')[0] ,'%b %d %Y %H')
	dt = datetime.fromtimestamp(mktime(stripped_time))
	t_delta = (datetime.now() - dt)
	if(t_delta.days <= 7):
		item_prices.append(steam_item[1])

#discard some outliers who lie more than 2 stdevs outside of mean
cleaned_data = reject_outliers(item_prices)

min_price = round(min(cleaned_data),2)
max_price = round(max(cleaned_data),2)
mean_price = round(mean(cleaned_data), 2)

print('Outliers cleaned: ')
print('min: $' + str(min_price))
print('max: $' + str(max_price))
print('mean: $' + str(mean_price))

#calculate fees, assuming you will be buying at the lowest and selling at the highest price
fees = min_price * 0.15
profit = max_price - min_price - fees
percent_gains = round(((profit / min_price) * 100),2)

print('Fees: $' + str(round(fees,2)))
print('Profit: $' + str(round(profit,2)))
print('Percent gains per buy/sell: ' + str(percent_gains) + '%')