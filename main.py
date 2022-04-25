import csv
import datetime
import time
import requests

BASE_LINK = "https://agsi.gie.eu/api"
ABOUT_LINK = "/about?show=listing"


def print_error_msg_and_ret_result(code, link):
    print('Ошибка получения данных, код ошибки:', code)
    time.sleep(1)
    print('Повтор последнего запроса...')
    return requests.get(link, timeout=15)


result = requests.get(BASE_LINK + ABOUT_LINK)
while result.status_code != 200:
    result = print_error_msg_and_ret_result(result.status_code, BASE_LINK + ABOUT_LINK)

print('Данные получены')
objects_json = result.json()

UGS_objects = []
for obj in objects_json:
    UGS_objects.append({'name': obj['name'], 'country': obj['country'], 'url': obj['url'], 'type': obj['type']})
    if len(obj) > 0:
        for ugs in obj['facilities']:
            UGS_objects.append({'name': ugs['name'], 'country': ugs['country'], 'url': ugs['url'], 'type': ugs['type']})

headers = ['Наименование и тип ПХГ', 'Статус', 'Дата', 'Газ в ПХГ', 'Заполнение', 'Изменение', 'Закачка', 'Отбор',
           'Рабочий объем', 'Макс.закачка', 'Макс.отбор', 'Страна', 'Тип', 'Номер строки']
load_date = (datetime.datetime.now() - datetime.timedelta(days=60)).strftime('%Y-%m-%d')
print('Получаем данные начиная с ', load_date)
with open('agsi.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(headers)
    for index, UGS in enumerate(UGS_objects):
        link = UGS['url'] + '&from=' + load_date + '&size=300'
        print(f'{index + 1} из, {len(UGS_objects)}, получение данных по ссылке:, {link}')
        result = requests.get(link)
        while result.status_code != 200:
            result = print_error_msg_and_ret_result(result.status_code, link)
        if 'error' in result.json():
            print('По ссылке получена ошибка, пропускаем данные.')
            continue
        for line in result.json()['data']:
            write_line = [UGS['name'], line['status'], line['gasDayStart'], line['gasInStorage'],
                          line['workingGasVolume'], line['trend'], line['injection'], line['withdrawal'],
                          line['workingGasVolume'], line['injectionCapacity'], line['withdrawalCapacity'],
                          UGS['country'], UGS['type'], index]
            writer.writerow(write_line)
