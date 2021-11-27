'''
2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы
(необходимо анализировать оба поля зарплаты). Для тех, кто выполнил задание с Росконтролем - напишите запрос для поиска
продуктов с рейтингом не ниже введенного или качеством не ниже введенного (то есть цифра вводится одна, а запрос
проверяет оба поля)
'''

from pymongo import MongoClient
from pprint import pprint


def find_vacancies_by_salary(salary, collection):
    for doc in collection.find({'$or': [{'minimum salary': {'$gt': salary}},
                                        {'maximum salary': {'$gt': salary}}]}):
        pprint(doc)


client = MongoClient('127.0.0.1', 27017)
db = client['vacancies']
engineers = db.engineers

user_salary = input('Введите минимальную зарплату, по которой вы хотите посмотреть вакансии: ')

while True:
    try:
        user_salary = int(user_salary)
        break
    except:
        user_salary = input('Вы ввели не число. Введите число: ')

find_vacancies_by_salary(user_salary, engineers)
