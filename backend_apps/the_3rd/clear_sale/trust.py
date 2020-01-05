# coding: utf-8

from datetime import datetime

from requests import post

API_AUTH = 'https://api.clearsale.com.br/v1/authenticate'
API_ENDPOINT = 'https://api.clearsale.com.br/v1/mobiletrust/transaction'
USER = 'Sofie'
PASS = 'on0HAjkeyR'


class ClearSaleAuth(object):
    """

    """

    def __init__(self):
        """
        Inicializa o objeto
        """
        self.__token = None
        self.__expiration_date = None

    def get_token(self):
        """
        Requisita um novo token ao ClearSale
        """
        resp = post(API_AUTH, data={'name': USER, 'password': PASS})
        if resp.status_code == 200:
            data = resp.json()
            self.__token = data['Token']
            self.__expiration_date = datetime.strptime(data['ExpirationDate'][0:19], '%Y-%m-%dT%H:%M:%S')

    def token_expired(self) -> bool:
        """

        :return:
        """
        return datetime.now() > self.__expiration_date

    @property
    def token(self):
        """
        Expõe o token, solicitando um novo caso necessário

        :return:
            `str`
        """
        if not self.__token or self.token_expired():
            self.get_token()

        return self.__token


class ClearSaleTrust(object):
    """

    """

    def __call__(self, token: str, document: str, document_type: str, phone: str, zip_code: str, email: str, transaction: str, description: str, price: float, consumer: str):
        """

        :param token:
        :param document:
        :param document_type:
        :param phone:
        :param zip_code:
        :param email:
        :param transaction:
        :param description:
        :param price:
        :param consumer:
        :return:
        """
        code_area = phone[0:2]
        cel_phone = phone[2:]

        data = {
            'Document': document,
            'DocumentType': document_type.upper(),
            'AreaCode': code_area,
            'Phone': cel_phone,
            'BlockSmsSending': True,
            'ZipCode': zip_code,
            'Email': email,
            'AdditionalInformation': {
                'Transaction': transaction,
                'Item': description,
                'Price': '{:.2f}'.format(price),
                'CustomerName': consumer,
                'Other': None
            }
        }

        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        resp = post(API_ENDPOINT, json=data, headers=headers)

        if resp.status_code == 401:
            pass

        return resp.json()


if __name__ == '__main__':
    clear_auth = ClearSaleAuth()
    print('TOKEN CLEAR SALE', clear_auth.token)

    clear_trust = ClearSaleTrust()
    clear_trust(
        token=clear_auth.token,
        document='19678335832',
        document_type='CPF',
        phone='11988056887',
        zip_code='06454050',
        email='jmarioguedes@gmail.com',
        transaction='123456789',
        description='Teste',
        price=1080.60,
        consumer='José Mario Silva Guedes'
    )
