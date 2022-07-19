import _sha256
import requests
import time

from datetime import date, datetime
from django.conf import settings
from xml.etree import ElementTree as ET

from .models import Order

# Словарь для записи значений, которые требуют постоянного обновления: курс доллара,
#                                                                      контрольная сумма,
#                                                                      сегодняшняя дата.
CACHE_VALUES = {
    'DOLLAR_CURRENCY': '',
    'CONTROL_SUM': '',
    'TODAY_DATE': '',
}
NUM_DIGITS = 4
SAMPLE_RANGE_NAME = 'Лист1'
SAMPLE_SPREADSHEET_ID = '1cZpLMr5_Sy8OIKXkFzetfetjf-RA6Stq6k3II0fD2P4'

def convert_dollar_to_ruble():
    """Возвращает курс доллара к рублю
    """
    today = date.today().strftime("%d/%m/%Y")
    response = requests.get(f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={today}")
    tree = ET.fromstring(response.content)
    for valute in tree.findall('Valute'):
        if valute.get('ID') == "R01235":
            dollar_ruble_currency = float(valute.find('Value').text.replace(',', '.'))
    return dollar_ruble_currency

def check_add():
    """Обновляет либо записывает, новые записи из таблицы, путем обработки всей таблицы
    если изменений нет, то функция, благодаря кэшируемой контрольной сумме, не выполнит запрос к БД

    Формат таблицы: (int, int, float, datetime.date: '%d.%m.%Y')
    Если запись даты отличается от заданного формата, произойдет ошибка
    Если в строке не хватает значение, то текущая строка будет пропущена
    """
    if CACHE_VALUES['TODAY_DATE'] != date.today():
        CACHE_VALUES['TODAY_DATE'] = date.today()
        CACHE_VALUES['DOLLAR_CURRENCY'] = convert_dollar_to_ruble()
    dollar_ruble_currency = CACHE_VALUES['DOLLAR_CURRENCY']
    sheet = settings.GOOGLE_SHEET_CONNECT['sheet']
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    result_table = [
        x for x in result['values'][1:] if len(x) == 4
    ]
    control_sum = _sha256.sha256(string=bytes(str(result_table), encoding='utf-8')).hexdigest()
    if control_sum != CACHE_VALUES['CONTROL_SUM']:
        CACHE_VALUES['CONTROL_SUM'] = control_sum
        order_create = []
        order_update = []
        exists_ids = Order.objects.values_list('order', flat=True)
        for r, order_id, dollar_cost, date_finish in result_table:
            order_id = int(order_id)
            dollar_cost = float(dollar_cost)
            date_finish = datetime.strptime(date_finish, '%d.%m.%Y').strftime('%Y-%m-%d')
            ruble_cost = round(dollar_ruble_currency * dollar_cost, NUM_DIGITS)
            if order_id not in exists_ids:
                order_create.append(
                    Order(order=order_id, dollar_cost=dollar_cost, ruble_cost=ruble_cost, date_finish=date_finish)
                )
            else:
                current_order = Order.objects.filter(order=order_id).first()
                current_order.order = order_id
                current_order.dollar_cost = dollar_cost
                current_order.ruble_cost = ruble_cost
                current_order.date_finish = date_finish
                order_update.append(current_order)
        if order_create:
            Order.objects.bulk_create(order_create)
        if order_update:
            Order.objects.bulk_update(order_update, fields=['order', 'dollar_cost', 'ruble_cost', 'date_finish'])
