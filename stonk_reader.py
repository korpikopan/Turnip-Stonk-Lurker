import json
import pandas as pd
import re
import time

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

import datetime

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

sheet = client.open('stonk_lurker').sheet1

pp = pprint.PrettyPrinter()
result = sheet.get_all_records()


def read_info(file,arg, num=0):
	data = open(file).read()
	liste = [row for row in data.split('\n')]

	return json.loads(liste[num]).get(arg, None)

def del_dodo(string):
	try:
		get = re.findall(r'[\d[a-zA-Z]{5}', string)
	except:
		get = ''

	for el in get:
		string = string.replace(el, '')
	return string

def del_mention(string):
	try:
		get = re.findall(r'@[\w]*', string)
	except:
		get = ''

	for el in get:
		string = string.replace(el, '')
	return string

def find_stonk(string):
	result = re.findall(r'\d{2,3}', string)
	result = [int(el) for el in result]
	result = max(result)
	return result

def update_spreadsheet(i, liste, time_sleep=10):
	screen_name, quoted_tweet, tweet, price, expanded_url, date, datetime = liste
	sheet.update_cell(i+2,1, screen_name)
	sheet.update_cell(i+2,2, quoted_tweet)
	sheet.update_cell(i+2,3, tweet)
	sheet.update_cell(i+2,4, price)
	sheet.update_cell(i+2,6, expanded_url)
	sheet.update_cell(i+2,7, date)
	sheet.update_cell(i+2,8, datetime)
		
	time.sleep(time_sleep)

def date_format(date):
	date = datetime.datetime.strptime(date, '%a %b %d %H:%M:%S +0000 %Y').strftime('%d/%m/%Y %H:%M:%S')
	date_jour, date_time = date.split(' ')
	heure, minute, seconde = date_time.split(':')
	heure = int(heure) + 2
	heure = str(heure)
	date_time = ':'.join([heure, minute, seconde])
	return date_jour, date_time

def generate_stonk(taille=15):
	df = pd.DataFrame(columns=['username', 'quote_tweet', 'tweet', 'price', 'url'])
	for i in range(taille):
		created_at = read_info('tweets.txt', 'created_at', num=i)
		date, datetime = date_format(created_at) 
		screen_name = read_info('tweets.txt', 'user', num=i)['screen_name']
		try:
			quoted_tweet = read_info('tweets.txt', 'quoted_status', num=i)['text']
			quoted_tweet_sansdodo = del_dodo(quoted_tweet)
			quoted_tweet_clean = del_mention(quoted_tweet_sansdodo)
			price_quote = find_stonk(quoted_tweet_clean)
		except:
			quoted_tweet = None
			price_quote = 0

		tweet = read_info('tweets.txt', 'text', num=i)
		tweet_sansdodo = del_dodo(tweet)
		tweet_clean = del_mention(tweet_sansdodo)
		try:
			price_tweet = find_stonk(tweet_clean)
		except:
			price_tweet = 0

		price = max(price_tweet, price_quote)
		try:
			expanded_url = read_info('tweets.txt', 'entities', num=i)['urls'][0]['expanded_url']
		except:
			expanded_url = None

		update_spreadsheet(i,[screen_name, quoted_tweet, tweet, price, expanded_url, date, datetime])