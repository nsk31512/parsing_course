'''
Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости.
 Для парсинга использовать XPath. Структура данных должна содержать:
название источника;
наименование новости;
ссылку на новость;
дата публикации.
Сложить собранные новости в БД
'''

#https://lenta.ru/rubrics/travel/

from lxml import html
import requests
from pprint import pprint
from pymongo import MongoClient
from pymongo import *
import re


#создание БД
client = MongoClient('127.0.0.1', 27017)
db = client['lenta_news']
news = db.news

#news.create_index([('link', pymongo.TEXT)], name='unique description', unique=True)

url = 'https://lenta.ru'
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

response = requests.get(url + '/rubrics/travel/', headers=header)
dom = html.fromstring(response.text)
links = dom.xpath('(//h1 | //h3)/../@href')
names = dom.xpath('(//h1 | //h3)/text()')
dates = dom.xpath('(//h1 | //h3)/../@href')

for i in range(len(links)):
    links[i] = url + links[i]

for i in range(len(names)):
    names[i] = names[i].replace('\xa0', ' ')

for i in range(len(dates)):
    dates[i] = re.search(r'\d{4}/\d\d/\d\d', dates[i])[0]

#объединение списков
zipped_data = list(zip(links, names, dates))
id_count = 0

#заполнение словаря перед для добавленияв БД
for i in range(len(zipped_data)):
    news_data = {'_id': id_count,
                 'link': zipped_data[i][0],
                 'name': zipped_data[i][1],
                 'date': zipped_data[i][2],
                 'source': url
                 }
    # заполнение БД
    news.update_one({'_id': id_count}, {'$set': news_data}, upsert=True)

for doc in news.find({}):
    pprint(doc)
