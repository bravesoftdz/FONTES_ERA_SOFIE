import json
from collections import namedtuple
from uuid import uuid1

from botocore.vendored import requests as requests


def lambda_handler(event, context):
    """
    Manipulador da chamada HTTP
    """

    params = json.loads(event.get('body'))

    status, data = TransactionFlow(**params)()

    return {
        'statusCode': status,
        'body': json.dumps(data)
    }


Transaction = namedtuple('Transaction', ('transaction_id', 'product_id', 'sofier', 'consumer', 'delivery_address', 'payment', 'execution_flow', 'production'))
Consumer = namedtuple('Consumer', ('document', 'name', 'email', 'birthdate', 'address'))
Address = namedtuple('Address', ('type', 'full_name', 'number', 'complement', 'district', 'city', 'state', 'country', 'reference', 'postal_code'))
Payment = namedtuple('Payment', ('modality', 'params'))
PaymentParams = namedtuple('Params', ('installments', 'credit_card'))
CreditCard = namedtuple('CreditCard', ('pin', 'holder', 'expiration', 'cvv', 'brand'))
Product = namedtuple('Product', ('product_id', 'value', 'reward', 'description'))


class TransactionFlow(object):
    """
    Fluxo de pagamento via cartão de crédito

    - QueryBin
    - Autorização
    - ClearSale
    - Captura
    - Crédito ao _sofier_
    - Cancelamento
    - Envio de eMail ao consumidor
    - Push Notification ao sofier
    - Guardar todos os dados no Dynamo na tabela `payments`
    """

    #: DEPLOY
    MERCHANT_ID = '10cfbea6-7ba9-46ad-8500-e03560fd015c'
    MERCHANT_KEY = 'Yt8g9zfhBIIR46fChldmREIxapaadASF2gVK0mn9'
    HOST_REQUEST = 'https://api.cieloecommerce.cielo.com.br/'
    HOST_QUERY = 'https://apiquery.cieloecommerce.cielo.com.br/'

    #: CLEAR SALE
    API_AUTH = 'https://api.clearsale.com.br/v1/authenticate'
    API_ENDPOINT = 'https://api.clearsale.com.br/v1/mobiletrust/transaction'
    USER = 'Sofie'
    PASS = 'on0HAjkeyR'

    #: CABEÇALHO PADRÃO
    HEADERS = {
        'merchantId': MERCHANT_ID,
        'merchantKey': MERCHANT_KEY,
        'Content-Type': 'application/json'
    }

    def __init__(self, **kwargs):
        """

        """
        super().__init__()

        self.__transaction = Transaction(
            transaction_id=str(uuid1()),
            product_id=kwargs['product_id'],
            sofier=kwargs['sofier'],
            consumer=Consumer(
                document=kwargs['consumer']['document'],
                name=kwargs['consumer']['name'],
                email=kwargs['consumer']['email'],
                birthdate=kwargs['consumer']['birthdate'],
                address=Address(**kwargs['consumer']['address'])
            ),
            delivery_address=Address(**kwargs['delivery_address']),
            payment=Payment(
                modality=kwargs['payment']['modality'],
                params=PaymentParams(
                    installments=kwargs['payment']['params']['installments'],
                    credit_card=CreditCard(**kwargs['payment']['params']['credit_card'])
                )
            ),
            execution_flow=kwargs['execution_flow'],
            production=Product(
                product_id='xxxxxxxxxxxxxxxxxxx',
                value=1,
                reward=.10,
                description='Produto de teste'
            )
        )

        self.__final_result = {'payment_info': kwargs}

    @property
    def transaction(self):
        """
        Expõe o objeto Transaction
        """
        return self.__transaction

    @property
    def final_result(self):
        """
        Expõe o objeto com o resultado final para a persistência
        """
        return self.__final_result

    def __call__(self) -> tuple:
        """
        Executa o fluxo completo de pagamento via cartão de crédito
        """
        try:
            #: QueryBin - Consultando aderência do cartão
            card_is_valid = self.query_bin()
            if not card_is_valid:
                return 400, {'message': 'Cartão de Crédito não reconhecido como tal'}

            #: Pré autorização
            was_authorized = self.authorization()
            if not was_authorized:
                return 400, {'message': 'Operação não autorizada'}

            #: Clear Sale

            #: Resultado final
            return 200, {'message': 'SUCCESS'}
        finally:
            #: Salvando no DynamoDB
            self.save_info()

    def query_bin(self) -> bool:
        """
        Consulta se um número de cartão de crédito esta apto a ser utilizado

        :return
            Indica o sucesso ou insucesso da operação
        """
        response = requests.get(f'{TransactionFlow.HOST_QUERY}/1/cardBin/{self.transaction.payment.params.credit_card.pin[:6]}', headers=TransactionFlow.HEADERS)
        data = response.json()
        self.final_result['query_bin'] = data

        return response.status_code == 200 and data['Status'] == '00' and data['CardType'] in ('Crédito', 'Multiplo')

    def authorization(self) -> bool:
        """
        Efetua a pré-autorização da operação para posterior captura

        :return
            Indica o sucesso ou insucesso da operação
        """
        transaction = self.transaction

        data_input = {
            'MerchantOrderId': transaction.transaction_id,
            'Customer': {
                'Name': transaction.consumer.name,
                'Email': transaction.consumer.email,
                'Birthdate': transaction.consumer.birthdate,
                'Address': {
                    'Street': f'{transaction.consumer.address.type} {transaction.consumer.address.full_name}',
                    'Number': transaction.consumer.address.number,
                    'Complement': transaction.consumer.address.complement,
                    'ZipCode': transaction.consumer.address.postal_code,
                    'City': transaction.consumer.address.city,
                    'State': transaction.consumer.address.state,
                    'Country': 'BRA'
                },
                'DeliveryAddress': {
                    'Street': f'{transaction.delivery_address.type} {transaction.delivery_address.full_name}',
                    'Number': transaction.delivery_address.number,
                    'Complement': transaction.delivery_address.complement,
                    'ZipCode': transaction.delivery_address.postal_code,
                    'City': transaction.delivery_address.city,
                    'State': transaction.delivery_address.state,
                    'Country': 'BRA'
                }
            },
            'Payment': {
                'Type': 'CreditCard',
                'Amount': ''.join('{:.2f}'.format(transaction.production.value).split('.')),  # <<<<
                'Currency': 'BRL',
                'Country': 'BRA',
                'ServiceTaxAmount': 0,
                'Installments': transaction.payment.params.installments,
                'Interest': 'ByMerchant',
                'Capture': False,
                'Authenticate': False,
                'SoftDescriptor': transaction.production.description[:13] or 'Sofie',
                'CreditCard': {
                    'CardNumber': transaction.payment.params.credit_card.pin,
                    'Holder': transaction.payment.params.credit_card.holder,
                    'ExpirationDate': transaction.payment.params.credit_card.expiration,
                    'SecurityCode': transaction.payment.params.credit_card.cvv,
                    'SaveCard': 'false',
                    'Brand': {'VISA': 'Visa', 'MASTERCARD': 'Master'}.get(transaction.payment.params.credit_card.brand, transaction.payment.params.credit_card.brand)
                }
            }
        }

        headers = TransactionFlow.HEADERS.copy()
        headers['RequestId'] = str(uuid1())
        response = requests.post(f'{TransactionFlow.HOST_REQUEST}/1/sales/', json=data_input, headers=headers)
        data = response.json()

        self.final_result['authorization'] = data

        return response.status_code == 201 and data['Payment']['ReturnCode'] == '00'

    def capture(self, payment_id: str) -> dict:
        """
        Efetua a captura do valor no cartão de crédito

        :param payment_id:
            ID da Transação na Cielo
        """
        headers = TransactionFlow.HEADERS.copy()
        headers['RequestId'] = str(uuid1())

        response = requests.put(f'{TransactionFlow.HOST_REQUEST}/1/sales/{payment_id}/capture', headers=headers)

        return response.json()

    def cancel(self, payment_id: str) -> dict:
        """
        Efetua o cancelamento do valor junto à Cielo

        :param payment_id:
            ID da Transação na Cielo
        """
        headers = TransactionFlow.HEADERS.copy()
        headers['RequestId'] = str(uuid1())

        response = requests.put(f'{TransactionFlow.HOST_REQUEST}/1/sales/{payment_id}/void', headers=headers)

        return response.json()

    def clear_sale(self, info: CreditCard) -> dict:
        """

        """
        pass

    def send_email(self, **kwargs) -> dict:
        """

        """
        pass

    def push_notification(self, **kwargs) -> dict:
        """

        """
        pass

    def save_info(self) -> bool:
        """

        :param data:
        :return:
        """
        pass


if __name__ == '__main__':
    BODY = {
        "product_id": "0000-0000-0000-0000",
        "sofier": "jmarioguedes@gmail.com",
        "consumer": {
            "document": "19678335832",
            "name": "José Mario Silva Guedes",
            "email": "jmarioguedes@gmail.com",
            "birthdate": "1977-09-08",
            "address": {
                "city": "Barueri",
                "complement": "APTO 93",
                "country": "Brasil",
                "district": "Alphaville Industrial",
                "full_name": "Grajaú",
                "number": "248",
                "postal_code": "06454050",
                "reference": "Em frente ao Cartório",
                "state": "SP",
                "type": "Alameda"
            }
        },
        "delivery_address": {
            "city": "Barueri",
            "complement": "APTO 93",
            "country": "Brasil",
            "district": "Alphaville Industrial",
            "full_name": "Grajaú",
            "number": "248",
            "postal_code": "06454050",
            "reference": "Em frente ao Cartório",
            "state": "SP",
            "type": "Alameda"
        },
        "payment": {
            "modality": "CREDIT_CARD",
            "params": {
                "installments": 1,
                "credit_card": {
                    "pin": "5149450628873588",
                    "holder": "JOSE MARIO SILVA GUEDES",
                    "expiration": "06/2027",
                    "cvv": "685",
                    "brand": "MASTERCARD"
                },
            }
        },
        "execution_flow": [{
            "question": "Qual é a sua idade?",
            "response": 21,
            "input_style": "input_number",
            "type_response": "string"
        }]
    }

    body2str = json.dumps(BODY).replace('"', '\\"')
    print(body2str)

    EVENT = {
        "body": json.dumps(BODY),
        "resource": "/{proxy+}",
        "path": "/path/to/resource",
        "httpMethod": "POST",
        "isBase64Encoded": False,
        "queryStringParameters": {
            "foo": "bar"
        },
        "pathParameters": {
            "proxy": "/path/to/resource"
        },
        "stageVariables": {
            "baz": "qux"
        },
        "headers": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-US,en;q=0.8",
            "Cache-Control": "max-age=0",
            "CloudFront-Forwarded-Proto": "https",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-Mobile-Viewer": "false",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Tablet-Viewer": "false",
            "CloudFront-Viewer-Country": "US",
            "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Custom User Agent String",
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "cDehVQoZnx43VYQb9j2-nvCh-9z396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https"
        },
        "requestContext": {
            "accountId": "123456789012",
            "resourceId": "123456",
            "stage": "prod",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "requestTime": "09/Apr/2015:12:34:56 +0000",
            "requestTimeEpoch": 1428582896000,
            "identity": {
                "cognitoIdentityPoolId": None,
                "accountId": None,
                "cognitoIdentityId": None,
                "caller": None,
                "accessKey": None,
                "sourceIp": "127.0.0.1",
                "cognitoAuthenticationType": None,
                "cognitoAuthenticationProvider": None,
                "userArn": None,
                "userAgent": "Custom User Agent String",
                "user": None
            },
            "path": "/prod/path/to/resource",
            "resourcePath": "/{proxy+}",
            "httpMethod": "POST",
            "apiId": "1234567890",
            "protocol": "HTTP/1.1"
        }
    }

    global_result = lambda_handler(EVENT, None)

    from pprint import pprint
    pprint(global_result['body'])
