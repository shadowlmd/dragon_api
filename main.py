import os
import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

DATE_FORMAT = "%Y-%m-%d"
# BEGIN_DATE = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime(DATE_FORMAT)
# END_DATE = datetime.datetime.today().strftime(DATE_FORMAT)
BEGIN_DATE = '2021-03-19'
END_DATE = '2021-03-20'
NO_MONEY_MESSAGE = 'Нет продаж по наличным за день'
SUCCESS_MESSAGE = 'Выгрузка успешна'
AQSI_URL = f'https://api.aqsi.ru/pub/v2/Receipts?filtered.BeginDate={BEGIN_DATE}&filtered.EndDate={END_DATE}&filtered.Operation=1'
AQSI_TOKEN = os.getenv('AQSI_TOKEN')
MOE_DELO_URL = 'https://restapi.moedelo.org/accounting/api/v1/cashier/1/retailRevenue'
MOE_DELO_TOKEN = os.getenv('MOE_DELO_TOKEN')


def get_orders():
    amount_rub = 0
    headers = {
        "x-client-key": AQSI_TOKEN
    }
    orders = requests.get(AQSI_URL, headers=headers).json()['rows']
    z = requests.get(AQSI_URL, headers=headers).json()['rows'][0]['shiftNumber']
    for i in range(len(orders)):
        if orders[i]['content']['checkClose']['payments'][0]['acquiringData'] is None:
            amount_rub += int(orders[i]['content']['checkClose']['payments'][0]['amount'])
    return amount_rub, z


def create_document(day_amount, z_number):

    if day_amount == 0:
        return NO_MONEY_MESSAGE
    else:
        headers = {
            "md-api-key": MOE_DELO_TOKEN
        }
        document = {
            "DocDate": BEGIN_DATE,
            "Description": f"Отчёт о продаже на точке Студия старинного танца Хрустальный дракон (ИНН=7804535190) на сумму {day_amount} руб",
            "Sum": day_amount,
            "ZReportNumber": z_number
        }
        requests.post(MOE_DELO_URL, data=document, headers=headers).json()
        return SUCCESS_MESSAGE


if __name__ == '__main__':
    print(create_document(get_orders()[0], get_orders()[1]))
