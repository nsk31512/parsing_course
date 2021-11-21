import requests
import hashlib

url = 'https://api.vk.com/method/'
method = 'groups.get'
access_token = '304cf33ce13e11f033fd5fce5950798e7bee189a081f8dc5243f3a7369422401ed750fd92cc7a223c28ba'
user_id = '13273613'
version = '5.131'
params = {
    'access_token': access_token,
    'user_id': user_id,
    'v': version
}

response = requests.get(url=url+method, params=params)

j_data = response.json()
h = hashlib.sha1()

with open('result_of_hometask1.txt', 'w', encoding='utf-8') as result_file:

    result_file.write(f'Пользователь VK {user_id} состоит в следующих сообществах:\n')
    for item in j_data.get('response').get('items'):
        h.update(b'item')
        item = h.hexdigest()
        result_file.write(f'{item};\n')

