
import requests
from bs4 import BeautifulSoup
import re

import datetime
import time
import os
import pandas as pd
# from multiprocessing.pool import ThreadPool
import logging
# In[2]:


# proxies = {'http': 'http://95.211.175.167:13151/', 'http': 'http://95.211.175.225:13151/'}
# proxies = {'http': 'http://108.59.14.200:13152/'}
thread_count = 2
# wd = '/home/ubuntu/scrape_use_request/'
# os.chdir(wd)
time_period = 60 * 1
start_date = '07-25-2006'
end_date = '12-31-2006'
saveDir = './playground'
log_location = './logs'


# In[3]:


def getFisrtHTMLByReq(data, logger):
    global session
    while True:
        try:
            session = requests.Session()
            firstPage = session.post(URL, data=data)
            break
        except Exception as e:
            # print("--------- Failed. page number : 1")
            logger.critical("--------- Failed. page number : 1")
            logger.critical(str(e))
            time.sleep(time_period)
            # print("========= Restarting request. page number : 1")
            logger.critical("========= Restarting request. page number : 1")
    return firstPage


# In[4]:


def getOtherHTMLByReq(param, page_index):
    global logger
    while True:
        try:
            # r = session.post(URL, params=param, proxies=proxies)
            r = session.post(URL, params=param)
            break
        except Exception as e:
            logger.critical("--------- Failed. page number : " + str(page_index))
            # print("--------- Failed. page number : " + str(page_index))
            # print(str(e))
            logger.critical(str(e))
            time.sleep(time_period)
            # print("========= Restarting request. page number : " + str(page_index))
            logger.critical("========= Restarting request. page number : " + str(page_index))
    return r


# In[5]:


def parseHTML(html):
    try:
        soup = BeautifulSoup(html, features='lxml')
    except Exception as e:
        print(e)
    return soup


# In[6]:


def getpage_counts(soup):
    ele_docsNum = soup.find('span', {"class": "basic-text-white"})
    if ele_docsNum:
        docsNum = ele_docsNum.get_text()
        result = docsNum.split(' ')
        resultNumber = int(result[-1])
        if (resultNumber % 10 == 0):
            page_counts = int(resultNumber / 10 - 1)
        else:
            page_counts = int(resultNumber / 10)
        return page_counts
    else:
        return 0


# In[7]:


# %%
def parseContent(soup):
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

        para = re.compile(r'\.\.+\D+\w+\D+').sub('', txt.get_text())
        temp = contents[counter]
        if words is None or words == []:
            temp.append(0)
        else:
            wordsNum = re.findall(r'\d*', words[0])
            temp.append(wordsNum[3])
        temp.append(para)
        counter += 1
    return contents


# In[8]:


def getPageContent(page_index):
    global logger
    a = time.time()
    topdoc = str(11 * page_index)
    param['p_action'] = 'list'
    param['p_topdoc'] = topdoc
    param['d_sources'] = 'location'
    page_raw = getOtherHTMLByReq(param, page_index)
    soup = parseHTML(page_raw.text)
    page_content_list = parseContent(soup)
    df_new = pd.DataFrame(page_content_list, columns=columns)
    logger.info("page number " + str(page_index + 1) + " of " + str(page_counts) + ": success ")
    return df_new


# In[9]:


def getBetweenDay(begin_date, end_date):
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%m-%d-%Y")
    end_date = datetime.datetime.strptime(end_date, "%m-%d-%Y")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)
    return date_list


# In[10]:


def create_logger(log_location, today_date, show_logs=True):
    logger = logging.getLogger(today_date)
    logger.setLevel(logging.DEBUG)
    if not os.path.exists(log_location):
        os.makedirs(log_location)
    log_file = "{0}{1}{2}{3}".format(log_location, os.path.sep, today_date, '.log')
    file_handler = logging.FileHandler(log_file)
    extra = {"today_date": today_date}
    logger_formatter = logging.Formatter(
        '%(levelname)s [%(asctime)s] [%(today_date)s]  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(logger_formatter)
    logger.addHandler(file_handler)
    if show_logs is True:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logger_formatter)
        logger.addHandler(console_handler)
    logger = logging.LoggerAdapter(logger, extra)
    return logger


# In[11]:


dates = getBetweenDay(start_date, end_date)
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

session = ''
for today_date in dates:
    logger = create_logger(log_location, today_date)
    logger.info("**** Started. Date : " + today_date)
    data['p_text_YMD_date-0'] = str(today_date)
    columns = ['office', 'date', 'author', 'words', 'paragraph']
    while True:
        firstPage = getFisrtHTMLByReq(data, logger)
        RESULTS_LIST = []

        soup1 = parseHTML(firstPage.text)
        page_counts = getpage_counts(soup1)
        if page_counts == 0:
            time.sleep(60 * 30)
            continue
        first_page_content_list = parseContent(soup1)
        df = pd.DataFrame(first_page_content_list, columns=columns)
        logger.info("page number 1 of " + str(page_counts) + ": success")
        page_number_list = list(range(1, page_counts))

        # with ThreadPool(thread_count) as my_thread_pool:
        #     RESULTS_LIST = my_thread_pool.map(getPageContent, page_number_list)
        # for RESULTS in RESULTS_LIST:
        #     df = pd.concat([df, RESULTS], ignore_index=True)

        for pageNum in page_number_list:
            results_onepage = getPageContent(pageNum)
            df = df.append(results_onepage, ignore_index=True)

        csv_filename = './' + str(today_date) + '.csv'
        df.to_csv(csv_filename, index=False)
        logger.info(str(today_date) + ": all success!")
        break

# In[ ]:
