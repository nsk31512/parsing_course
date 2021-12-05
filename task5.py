'''
Написать программу, которая собирает товары «В тренде» с сайта техники mvideo и складывает данные в БД. Сайт можно
выбрать и свой. Главный критерий выбора: динамически загружаемые товары
'''


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from pymongo import *


url = 'https://www.mvideo.ru/'
chrome_options = Options()
chrome_options.add_argument('--start-maximized')
driver = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)
driver.get(url)

actions = ActionChains(driver)
actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN)
actions.perform()
driver.implicitly_wait(10)

#выбор раздела с товарами "В тренде"
box = driver.find_element(By.XPATH, "//mvid-shelf-group[contains(@class, 'page-carousel-padding ng-star-inserted')]")
button = box.find_element(By.XPATH, ".//button[contains(@class, 'tab')][2]")
button.click()

names = box.find_elements(By.XPATH, ".//div[contains(@class, 'name')]//a")
names_list = []
links_list = []
for name in names:
    names_list.append(name.text)
    links_list.append(name.get_attribute('href'))

prices = box.find_elements(By.XPATH, ".//div[contains(@class, 'price')]//span[contains(@class, 'main-value') and not(position() = 2)]")
prices_list = []
for price in prices:
    prices_list.append(float(price.text.replace(' ', '')))

zipped_data = list(zip(names_list, links_list, prices_list))

driver.quit()

#создание БД
client = MongoClient('127.0.0.1', 27017)
db = client['mvideo_products']
trend_products = db.trend_products

for i in range(len(zipped_data)):
    product_dict = {
        '_id': i,
        'name': zipped_data[i][0],
        'link': zipped_data[i][1],
        'price': zipped_data[i][2],
        'currency': 'RUB',
        'source': url
    }

    trend_products.update_one({'_id': i}, {'$set': product_dict}, upsert=True)

for doc in trend_products.find({}):
    print(doc)

