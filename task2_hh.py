'''
Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы получаем
должность) с сайтов HH(обязательно) и/или Superjob(по желанию). Приложение должно анализировать несколько страниц сайта
(также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:

Наименование вакансии.
Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
Ссылку на саму вакансию.
Сайт, откуда собрана вакансия.

По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть
одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas. Сохраните в
json либо csv.
'''

#https://novosibirsk.hh.ru/search/vacancy?area=4&fromSearchLine=true&text=Инженер-проектировщик&from=suggest_post&page=0

import requests
from bs4 import BeautifulSoup
from pprint import pprint
import sys
import pandas as pd


# вводим должность поискового запроса
request_name = input('Введите желаемую вакансию: ')

url = 'https://novosibirsk.hh.ru'

params = {
    'area': 4,
    'fromSearchLine': True,
    'text': request_name,
    'from': 'suggest_post'
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 OPR/81.0.4196.60 (Edition Yx 05)'}

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

vacancy_list = []

for num in range(number_of_page_for_searching):
    params = {
        'area': 4,
        'fromSearchLine': True,
        'text': request_name,
        'from': 'suggest_post',
        'page': num
    }
    response = requests.get(url + '/search/vacancy', params=params, headers=headers)
    dom = BeautifulSoup(response.text, 'html.parser')
    vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancies:
        vacancy_data = {}
        name = vacancy.find('a')
        link = name.get('href')
        name_vacancy = name.text
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

        vacancy_data['vacancy name'] = name_vacancy
        vacancy_data['link'] = link
        vacancy_data['minimum salary'] = salary_min
        vacancy_data['maximum salary'] = salary_max
        vacancy_data['currency'] = currency
        vacancy_data['Web-Site'] = 'hh.ru'
        vacancy_list.append(vacancy_data)

vacancy_list = pd.Series(vacancy_list)
vacancy_list.to_json('task2_result.json', orient='records', force_ascii=False, lines=True)
