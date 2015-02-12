#!/usr/bin/python3.4
import requests, sys, matplotlib, datetime, os.path, json, numpy

database_url = 'http://104.236.192.200:5984/tracked_steam_item_stats/'
document_name = '2015-02-12%2007%3A12%3A40.975307'


def import_graph_json():
	#Holds steam market item data, including graph data-points.
	market_data_request = None 
	market_data_json = None

	#Check for cached data
	if os.path.isfile('graph-data-cache.json'):
		print("Reading cached data...")
		cache = open('graph-data-cache.json', 'r')
		market_data_json = json.loads(cache.read())
	else:
		#Request a document containing item graph data.
		print("Downloading data...")
		try: 
			market_data_request = requests.get(database_url + document_name)
			market_data_request.raise_for_status() #Raise exception if HTTP error occurred
		except Exception as http_exception: 
			print(http_exception) 
			sys.exit()

		#Convert response to JSON
		try: 
			market_data_json = market_data_request.json().get('steam_items') #convert request to json.
			cache = open('graph-data-cache.json', 'w')
			json.dump(market_data_json, cache)
		except Exception as parsing_exception:
			print(parsing_exception)
			sys.exit()

	return market_data_json

def json_to_points(data_json):
	from datetime import datetime

	graph_data_aggregate = []

	for market_item in data_json:
		market_item_name = market_item.get('name')
		graph_points = market_item.get('graph_points')

		dates = []
		prices = []

		for date, price in graph_points.items():
			dates.append(datetime.strptime(date, "%Y-%m-%d %H:%M:%S"))
			prices.append(price)

		graph_data_aggregate.append({'name':market_item_name, 'prices':prices ,'dates':dates})

	return graph_data_aggregate

def poly_calc(graph_data, poly_degree=1):
	from matplotlib import pyplot
	from matplotlib.dates import date2num

	graph_data['dates'] = date2num(graph_data['dates'])

	coefficients = numpy.polyfit(graph_data['dates'], graph_data['prices'], poly_degree)
	polynomial = numpy.poly1d(coefficients)

	return polynomial

def poly_plot(graph_data, poly_degree=1, buy_price=None, sell_price=None):
	from matplotlib import pyplot
	from matplotlib.dates import date2num



	poly_y = graph_data['polynomial'](graph_data['dates'])
	pyplot.plot_date(graph_data['dates'], graph_data['prices'], 'o')
	pyplot.plot_date(graph_data['dates'], poly_y, 'g-')
	if not buy_price is None:
		pyplot.axhline(y=buy_price, linewidth=1, color = 'k')
		#pyplot.plot_date(graph_data['dates'], buy_y, 'g-')
	if not sell_price is None:
		pyplot.axhline(y=sell_price, linewidth=1, color = 'k')
		#pyplot.plot_date(graph_data['dates'], buy_y, 'g-')
	pyplot.ylabel('y')
	pyplot.xlabel('x')
	pyplot.title(graph_data['name'])
	pyplot.show()

def search_graph_data(graph_data_aggregate, query=None, limit=30):
	display_options = []

	if query is None: query = input('Search query: ')
	for graph_data in graph_data_aggregate:
		if query.lower() in graph_data['name'].lower():
			display_options.append(graph_data)
	if(len(display_options) <= limit and len(display_options) > 0):
		count = 0
		for display_option in display_options:
			print('[' + str(count) + ']' + ' - ' + display_option['name'])
			count += 1
		try: 
			selection = int(input('\nSelection: '))
		except Exception:
			print('Please enter an index.')
			return False
		if (selection + 1) > len(display_options) or selection < 0:
			print('Not in range.')
			return False
		else:
			return display_options[selection]
	else:
		print(str(len(display_options)) + ' matches found. Narrow query.')
		return False

def get_buy_sell(graph_data, m=1.5):
	from statistics import mean, stdev

	data_mean = mean(graph_data['prices'])
	stdev = stdev(graph_data['prices'])

	buy_price = data_mean - (stdev * m)
	sell_price = data_mean + (stdev * m)

	return buy_price, sell_price

#Needs fixing before deployment
def remove_outliers(graph_data, m=2):
	from statistics import mean, stdev

	#Isolate price data for preliminary mean and stdev calculation
	prices = []

	for price in graph_data['prices']:
		prices.append(price)

	data_mean = mean(prices)
	data_stdev = stdev(prices)
	good_data = []

	#Generate a new prices and dates list
	trimmed_prices = []
	trimmed_dates = []
	for price, date in zip(graph_data['prices'], graph_data['dates']):
		#if the distance from the mean is < 2x the stdev, keep the data
		if(abs(price - data_mean) < (m * data_stdev)):
			trimmed_prices.append(price)
			trimmed_dates.append(date)
	
	graph_data['prices'] = trimmed_prices
	graph_data['dates'] = trimmed_dates

	return graph_data

#def get_buy_sell_prices(graph_data_aggregate, remove_outliers=True):
	

def main():
	from datetime import timedelta

	market_data_json = import_graph_json()
	graph_data_aggregate = json_to_points(market_data_json)

	#graph_data_aggregate = filter_by_time_delta(graph_data_aggregate, timedelta(days=3))

	graph_date_aggregate_filtered = []

	#Run poly calc on all items in aggregate
	#for graph_data in graph_data_aggregate:
	#	graph_date_aggregate_filtered.append(remove_outliers(graph_data))

	#for graph_data in graph_date_aggregate_filtered:
	#	graph_data['polynomial'] = poly_calc(graph_data)

	for graph_data in graph_data_aggregate:
		buy_price, sell_price = get_buy_sell(graph_data)
		graph_data['buy_price'] = buy_price
		graph_data['sell_price'] = sell_price
		graph_data['polynomial'] = poly_calc(graph_data)
	
	#Sort with lambda function to select appropriate sorting key
	graph_data_aggregate = sorted(graph_data_aggregate, key=lambda k: k['polynomial'][0])
	#graph_data_aggregate_filtered = sorted(graph_data_aggregate_filtered, key=lambda k: k['polynomial'][0]) 

	print('Index: 0-' + str(len(graph_data_aggregate) - 1))
	while True:
		search_request = int(input('Show result #: ' ))
		print(graph_data_aggregate[search_request]['polynomial'])
		buy_at = graph_data_aggregate[search_request]['buy_price']
		sell_at = graph_data_aggregate[search_request]['sell_price']
		poly_plot(graph_data_aggregate[search_request], 1, buy_price=buy_at, sell_price=sell_at)
		#print(graph_data_aggregate_filtered[search_request]['polynomial'])
		#poly_plot(graph_data_aggregate_filtered[search_request], 1)

if __name__ == '__main__':
	main()