# coding: utf-8

from http import HTTPStatus
from requests import get, put, post
from uuid import uuid1

from micro_contract.transaction import Transaction
from the_3rd.cielo.tables import BIN_ANALYSIS

#: DEVELOPER
# MERCHANT_ID = '5f8b7ad9-8ecd-41b0-b9fa-76c78f1faefe'
# MERCHANT_KEY = 'UZTOVFUZIHITGVSCWQWFHFDCCIJDXDSUOOPCCBYW'
# HOST_REQUEST = 'https://apisandbox.cieloecommerce.cielo.com.br'
# HOST_QUERY = 'https://apiquerysandbox.cieloecommerce.cielo.com.br'

#: DEPLOY
MERCHANT_ID = '10cfbea6-7ba9-46ad-8500-e03560fd015c'
MERCHANT_KEY = 'Yt8g9zfhBIIR46fChldmREIxapaadASF2gVK0mn9'
HOST_REQUEST = 'https://api.cieloecommerce.cielo.com.br/'
HOST_QUERY = 'https://apiquery.cieloecommerce.cielo.com.br/'


def query_bin(number: str) -> dict:
    """
    Consulta se um número de cartão é de crédito e apto a ser utilizado

    :param number:
        Número do cartão de crédito a ser analisado
    :return:
        `dict` com a resposta final
    """
    buffer = {
        'is_valid': False,
        'provider': None,
        'reason': None,
        'acquirer_data': None
    }

    headers = {
        'merchantId': MERCHANT_ID,
        'merchantKey': MERCHANT_KEY,
        'Content-Type': 'application/json'
    }

    response = get(f'{HOST_QUERY}/1/cardBin/{number[:6]}', headers=headers)

    if response.status_code == HTTPStatus.OK.value:
        acquirer_data = response.json()
        if acquirer_data['Status'] == '00' and acquirer_data['CardType'] in ('Crédito', 'Multiplo'):
            buffer['is_valid'] = True
            buffer['provider'] = acquirer_data['Provider']
        else:
            buffer['reason'] = '{} - {} - {}'.format(
                acquirer_data['Status'],
                BIN_ANALYSIS.get(acquirer_data['Status'], 'Status não definido'),
                acquirer_data['CardType']
            )

        buffer['acquirer_data'] = acquirer_data
    else:
        buffer['is_valid'] = True
        buffer['provider'] = 'Cielo'
        buffer['reason'] = 'Problemas de comunicação com a adquirente'
        buffer['acquirer_data'] = f'{response.status_code} - {response.reason}'

    return buffer


def authorization(transaction: str, number: str, cvv: str, brand: str, expiration: str, holder: str, value: float, installments: int, soft_description: str) -> dict:
    """

    :param transaction:
    :param number:
    :param cvv:
    :param brand:
    :param expiration:
    :param holder:
    :param value:
    :param installments:
    :param soft_description:
    :return:
    """
    transaction_obj = Transaction(transaction)

    headers = {
        'merchantId': MERCHANT_ID,
        'merchantKey': MERCHANT_KEY,
        'Content-Type': 'application/json',
        'RequestId': str(uuid1())
    }

    data_input = {
        'MerchantOrderId': transaction,
        'Customer': {
            'Name': transaction_obj.consumer.full_name,
            'Email': transaction_obj.consumer.email,
            'Birthdate': transaction_obj.consumer.birthday.strftime('%Y-%m-%d'),
            'Address': {
                'Street': '{} {}'.format(transaction_obj.address.type, transaction_obj.address.full_name),
                'Number': transaction_obj.address.number,
                'Complement': transaction_obj.address.complement,
                'ZipCode': transaction_obj.address.zipcode,
                'City': transaction_obj.address.city,
                'State': transaction_obj.address.state,
                'Country': 'BRA'
            },
            'DeliveryAddress': {
                'Street': '{} {}'.format(transaction_obj.address.type, transaction_obj.address.full_name),
                'Number': transaction_obj.address.number,
                'Complement': transaction_obj.address.complement,
                'ZipCode': transaction_obj.address.zipcode,
                'City': transaction_obj.address.city,
                'State': transaction_obj.address.state,
                'Country': 'BRA'
            }
        },
        'Payment': {
            'Type': 'CreditCard',
            'Amount': ''.join('{:.2f}'.format(value).split('.')),
            'Currency': 'BRL',
            'Country': 'BRA',
            'ServiceTaxAmount': 0,
            'Installments': installments,
            'Interest': 'ByMerchant',
            'Capture': False,
            'Authenticate': False,
            'SoftDescriptor': soft_description[:13] or 'Sofie',
            'CreditCard': {
                'CardNumber': number,
                'Holder': holder,
                'ExpirationDate': expiration,
                'SecurityCode': cvv,
                'SaveCard': 'false',
                'Brand': brand
            }
        }
    }

    url = '{host}/{resource}'.format(host=HOST_REQUEST, resource='1/sales/')

    response = post(url, json=data_input, headers=headers)

    return response.json()


def capture(payment_id: str) -> dict:
    """

    :param payment_id:
    :return:
    """
    headers = {
        'merchantId': MERCHANT_ID,
        'merchantKey': MERCHANT_KEY,
        'Content-Type': 'application/json',
        'RequestId': str(uuid1())
    }

    url = '{host}/{resource}'.format(host=HOST_REQUEST, resource='1/sales/{}/capture'.format(payment_id))

    response = put(url, headers=headers)

    return response.json()


def cancel(payment_id: str) -> dict:
    """

    :param payment_id:
    :return:
    """
    headers = {
        'merchantId': MERCHANT_ID,
        'merchantKey': MERCHANT_KEY,
        'Content-Type': 'application/json',
        'RequestId': str(uuid1())
    }

    url = '{host}/{resource}'.format(host=HOST_REQUEST, resource='1/sales/{}/void'.format(payment_id))

    response = put(url, headers=headers)

    return response.json()
