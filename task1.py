'''
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, которая будет добавлять
только новые вакансии/продукты в вашу базу.
'''
import pymongo
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import sys
import pandas as pd
from pymongo import MongoClient
from pymongo import *

#создание БД
client = MongoClient('127.0.0.1', 27017)
db = client['vacancies']
engineers = db.engineers
engineers.create_index([('description', pymongo.TEXT)], name='unique description', unique=True)

# вводим должность поискового запроса
request_name = input('Введите желаемую вакансию: ')
url = 'https://novosibirsk.hh.ru'
params = {
    'area': 4,
    'fromSearchLine': True,
    'text': request_name,
    'from': 'suggest_post',
    'items_on_page': 20
}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0'}

response = requests.get(url + '/search/vacancy', params=params, headers=headers)
dom = BeautifulSoup(response.text, 'html.parser')

#запрос количества просматриваемых страниц с проверкой на правильность введенной вакансии
try:
    number_of_pages = dom.find_all('span', {'class': 'pager-item-not-in-short-range'})[-1].text
    number_of_page_for_searching = input(f'С заданными условиями поиска найдено {number_of_pages} страниц вакансий. '
                                             'Введите число страниц, которое вы хотите посмотреть: ')
except:
    print('С заданными условиями поиска вакансий не найдено')
    sys.exit()

while True:
    try:
        number_of_page_for_searching = int(number_of_page_for_searching)
        break
    except:
        number_of_page_for_searching = input('Вы ввели не число. Введите число страниц: ')

if number_of_page_for_searching > int(number_of_pages):
    print(f'Вы ввели число страниц больше, чем найдено. Поиск будет осуществлен на {number_of_pages} страницах')
    number_of_page_for_searching = int(number_of_pages)

#счетчик вновь добавленных ваканчий
count_new = 0
#счетчик существующих ваканчий
count_old = 0
#уточнение параметров запроса
for num in range(number_of_page_for_searching):
    params = {
        'area': 4,
        'fromSearchLine': True,
        'text': request_name,
        'from': 'suggest_post',
        'page': num,
        'items_on_page': 20
    }
    response = requests.get(url + '/search/vacancy', params=params, headers=headers)
    dom = BeautifulSoup(response.text, 'html.parser')
    vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})

#сбор данных
    for vacancy in vacancies:
        vacancy_data = {}
        name = vacancy.find('a')
        link = name.get('href')
        name_vacancy = name.text
        description = vacancy.find('div', {'class': 'bloko-text',
                                           'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'})
        if description is None:
            description = f'Описание вакансии {name_vacancy} отсутствует'

        else:
            description = description.text
        salary = vacancy.find('div', {'class': 'vacancy-serp-item__sidebar'})
        try:
            salary = salary.find('span').text.replace('\u202f', '')
            salary_list = salary.split()
            salary_min = None
            salary_max = None
            currency = None
            for i in range(len(salary_list)):
                if salary_list[0] == 'от':
                    salary_min = int(salary_list[1])
                    currency = salary_list[-1]
                    break
                elif salary_list[0] == 'до':
                    salary_max = int(salary_list[1])
                    currency = salary_list[-1]
                    break
                else:
                    salary_min = int(salary_list[0])
                    salary_max = int(salary_list[-2])
                    currency = salary_list[-1]
                    break
        except:
            salary_min = None
            salary_max = None
            currency = None

        #заполнение данных словаря
        vacancy_data['vacancy name'] = name_vacancy
        vacancy_data['link'] = link
        vacancy_data['description'] = description
        vacancy_data['minimum salary'] = salary_min
        vacancy_data['maximum salary'] = salary_max
        vacancy_data['currency'] = currency
        vacancy_data['Web-Site'] = 'hh.ru'

        #заполнение БД
        try:
            engineers.insert_one(vacancy_data)
            count_new += 1
        except:
            count_old += 1

print(f'Добавлено {count_new} новых вакансий. Существующие {count_old} вакансий без изменений')

for doc in engineers.find({}):
    pprint(doc)






