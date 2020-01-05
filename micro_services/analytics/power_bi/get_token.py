# coding: utf-8

from datetime import datetime

from requests import post

API_AUTH = 'https://login.windows.net/common/oauth2/token'
CLIENT_ID = 'f9ad81ca-ffc5-4eae-92e1-92822f9b66f1'
GRANT_TYPE = 'password'
USERNAME = 'developer@mysofielabs.com'
PASSWORD = 'Dev@mysofie'
RESOURCE = 'https://analysis.windows.net/powerbi/api'


class PowerBIAuth(object):
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
        resp = post(
            API_AUTH,
            data={
                'client_id': CLIENT_ID,
                'grant_type': GRANT_TYPE,
                'username': USERNAME,
                'password': PASSWORD,
                'resource': RESOURCE
            })
        if resp.status_code == 200:
            data = resp.json()
            self.__token = data['access_token']
            self.__expiration_date = datetime.utcfromtimestamp(int(data['expires_on']))

    def token_expired(self) -> bool:
        """

        :return:
        """
        return datetime.utcnow() > self.__expiration_date

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


if __name__ == '__main__':
    powerbi_auth = PowerBIAuth()
    print('TOKEN POWER BI', powerbi_auth.token, '\n'
                                                'ExpiresDate', powerbi_auth.token_expired())
