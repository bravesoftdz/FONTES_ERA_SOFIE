# coding: utf-8

"""

"""

from json import dumps

from requests import post

URL_ZENVIA = 'https://api-rest.zenvia.com/services/send-sms'
USER = 'g4'
PSW = 'RXZUQFY6Sy'


class SMSSender(object):
    """

    """

    def __call__(self, to: str, msg: str, transaction: str):
        """

        :return:
        """
        try:
            if not to.startswith('55'):
                to = '55' + to

            if len(msg) > 140:
                raise Exception('A mensagem é maior que os 140 caracteres suportado pelo Zenvia')

            content = {
                'sendSmsRequest': {
                    'from': 'Sofie Pay',
                    'to': to,
                    'msg': msg,
                    'id': transaction
                }
            }

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            response = post(URL_ZENVIA, data=dumps(content), headers=headers, auth=(USER, PSW))

            return response.json()
        except Exception as err:
            pass


if __name__ == '__main__':
    sms = SMSSender()
    sms('11988056887', 'Olá Mundo!', '1654654654654654')
