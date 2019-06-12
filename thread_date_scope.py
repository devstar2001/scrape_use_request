# %%
import urllib.request
import requests
import webbrowser
from bs4 import BeautifulSoup
from joblib import Parallel, delayed
import multiprocessing
import re
import sys
import json
import datetime
import time
import os
import random
import pandas as pd
import zipfile
from multiprocessing.pool import ThreadPool


def getFisrtHTMLByReq(data):
	global session
	while True:
		try:
			session = requests.Session()
			firstPage = session.post(URL, data=data)
			break
		except Exception as e:
			print("--------- Failed. page number : 1")
			print(str(e))
			time.sleep(60 * 1)
			print("========= Restarting request. page number : 1")
			print(str(e))

	return firstPage


# %%
# With proxies
def getOtherHTMLByReq(param, page_index):
	while True:
		try:
			r = session.post(URL, params=param, proxies=proxies)
			break
		except Exception as e:
			print("--------- Failed. page number : " + str(page_index))
			print(str(e))
			time.sleep(60*1)
			print("========= Restarting request. page number : " + str(page_index))

	return r


# %%
def parseHTML(html):
	try:
		soup = BeautifulSoup(html, features='lxml')
	except Exception as e:
		print(e)
	return soup


# %%
def getpage_counts(soup):
	# start = time.time()
	docsNum = soup.find('span', {"class": "basic-text-white"}).get_text()
	result = docsNum.split(' ')
	resultNumber = int(result[-1])
	# e.g. 168 docs, 16.8 = 17 pages, no = 161
	# result = xx docs, page_counts: real pages number - 1,
	# result[-1]/10 = 16.8, page_counts=16
	# 30 and 35 have differences
	if (resultNumber % 10 == 0):
		page_counts = int(resultNumber / 10 - 1)
	else:
		page_counts = int(resultNumber / 10)
	return page_counts


# %%
def parseContent(soup):
	# start = time.time()
	text = soup.find_all('td', {"class": "basic-title"})

	contents = []
	for txt in text[::2]:
		office = re.compile(r'-.*\s*.*').sub('', txt.get_text())
		# Why is temp defined already here
		temp = re.compile(r'^.*-\s').sub('', txt.get_text())
		date_raw = re.compile(r'\n\w.*').sub('', temp).strip()
		try:
			date, date2 = date_raw.split('\n', 1)
		except:
			date = date_raw
		author = re.compile(r'.*\n').sub('', txt.get_text())

		# New: clean the strings (e.g., eliminate \n and \t)
		office = ''.join(c for c in office if c not in "\n'\t")
		date = ''.join(c for c in date if c not in "\n'\t")
		author = ''.join(c for c in author if c not in "\n'\t")

		office = ''.join(c for c in office if c not in '"')
		date = ''.join(c for c in date if c not in '"')
		author = ''.join(c for c in author if c not in '"')

		content = [office, date, author]
		contents.append(content)

	counter = 0
	for txt in text[1::2]:
		words = re.findall(r'of\s\d*\swords', txt.get_text())
		wordsNum = re.findall(r'\d*', words[0])
		para = re.compile(r'\.\.+\D+\w+\D+').sub('', txt.get_text())
		temp = contents[counter]
		temp.append(wordsNum[3])
		temp.append(para)
		counter += 1
	return contents


def getPageContent(page_index):
	a = time.time()
	topdoc = str(11 * page_index)
	param['p_action'] = 'list'
	param['p_topdoc'] = topdoc
	param['d_sources'] = 'location'
	page_raw = getOtherHTMLByReq(param, page_index)
	soup = parseHTML(page_raw.text)
	page_content_list = parseContent(soup)
	df_new = pd.DataFrame(page_content_list, columns=columns)
	print("page number " + str(page_index + 1) + " of " + str(page_counts) + ": success \n")
	print("~~~~~ " + str(time.time() - a))
	return df_new


# %%
def getBetweenDay(begin_date, end_date):
	date_list = []
	begin_date = datetime.datetime.strptime(begin_date, "%m-%d-%Y")
	end_date = datetime.datetime.strptime(end_date, "%m-%d-%Y")
	# end_date = datetime.datetime.strptime(time.strftime('%m-%d-%Y',time.localtime(time.time())), "%m-%d-%Y")
	while begin_date <= end_date:
		date_str = begin_date.strftime("%m-%d-%Y")
		date_list.append(date_str)
		begin_date += datetime.timedelta(days=1)
	return date_list


# %%
# os.chdir('/Users/philine/Dropbox/newslibrary_project/playground')
# %%
# With proxies


# %%
# Define dates which should be scraped
# today_date = datetime.datetime.now().strftime("%m-%d-%Y")

proxies = {'http': 'http://95.211.175.167:13151/', 'http': 'http://95.211.175.225:13151/'}
today_date = '01-01-1989'

saveDir = './playground'
if not os.path.exists(saveDir):
	os.mkdir(saveDir)
os.chdir(saveDir)
URL = 'https://nl.newsbank.com/nl-search/we/Archives'
data = {"s_siteloc": "NL2", "p_queryname": "4000", "p_action": "search", "p_product": "NewsLibrary",
		"p_theme": "newslibrary2", "s_search_type": "customized", "d_sources": "location",
		"d_place": 'United States', "p_nbid": "", 'p_field_psudo-sort-0': 'psudo-sort',
		"f_multi": '', "p_multi": "NewsLibraryAll", 'p_widesearch': 'smart', 'p_sort': 'YMD_date:D',
		"p_maxdocs": "200", "p_perpage": "10", 'p_text_base-0': '', 'p_field_base-0': '', 'p_bool_base-1': 'AND',
		'p_text_base-1': '', "p_field_base-1": '', 'p_bool_base-2': 'AND', 'p_text_base-2': '',
		'p_field_base-2': '', 'p_text_YMD_date-0': "01-01-2005", 'p_field_YMD_date-0': 'YMD_date',
		'p_params_YMD_date-0': "date:B,E", "p_field_YMD_date-3": "YMD_date", 'p_params_YMD_date-3': 'date:B,E',
		'Search.x': '42', "Search.y": '11'}
param = {'p_action': 'list', 'p_topdoc': '11', 'd_sources': 'location'}
dates = getBetweenDay('01-01-1989', '01-02-1989')
thread_count = 2
time_period = 60 * 1
session = ''
for today_date in dates:
	print("**** Started. Date : " + today_date)
	data['p_text_YMD_date-0'] = str(today_date)
	columns = ['office', 'date', 'author', 'words', 'paragraph']
	while True:
		firstPage = getFisrtHTMLByReq(data)
		RESULTS_LIST = []

		soup1 = parseHTML(firstPage.text)
		page_counts = getpage_counts(soup1)
		first_page_content_list = parseContent(soup1)
		df = pd.DataFrame(first_page_content_list, columns=columns)
		print("page number 1 of " + str(page_counts) + ": success \n")
		page_number_list = list(range(1, page_counts))
		# page_number_list = list(range(1, 25))

		with ThreadPool(thread_count) as my_thread_pool:
			RESULTS_LIST = my_thread_pool.map(getPageContent, page_number_list)

		for RESULTS in RESULTS_LIST:
			df = pd.concat([df, RESULTS], ignore_index=True)
		csv_filename = './' + str(today_date) + '.csv'
		df.to_csv(csv_filename, index=False)
		print(str(today_date) + ": all success!")
		break
