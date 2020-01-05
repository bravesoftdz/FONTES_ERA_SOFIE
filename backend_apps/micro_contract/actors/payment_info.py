# coding: utf-8

"""
Aglutina as classes auxiliares para lidar com as informações de pagamento
"""


class Validation(object):
    """

    """

    def __init__(self, *args):
        """

        :param args:
        """
        self.valid = args[0]
        self.when = args[1]
        self.log = args[2]


class Authorization(object):
    """

    """

    def __init__(self, *args):
        """

        :param args:
        """
        self.authorized = args[0]
        self.when = args[1]
        self.log = args[2]


class Catch(object):
    """

    """

    def __init__(self, *args):
        """

        :param args:
        """
        self.captured = args[0]
        self.when = args[1]
        self.log = args[2]


class Cancellation(object):
    """

    """

    def __init__(self, *args):
        """

        :param args:
        """
        self.canceled = args[0]
        self.when = args[1]
        self.log = args[2]


class CreditCardInfo(object):
    """
    Informações referente às transações com o cartão de crédito
    """

    def __init__(self, soul: dict):
        """
        Inicializa o objeto

        :param soul:
            Dicionário que representa as informações do pagamento
        """
        self.__soul = soul

        validation = self.__soul['validation']
        self.__validation_obj = Validation(validation['valid'], validation['when'], validation['log'])

        authorization = self.__soul['authorization']
        self.__authorization_obj = Authorization(authorization['authorized'], authorization['when'], authorization['log'])

        catch = self.__soul['catch']
        self.__catch_obj = Catch(catch['captured'], catch['when'], catch['log'])

        cancellation = self.__soul['cancellation']
        self.__cancellation_obj = Cancellation(cancellation['canceled'], cancellation['when'], cancellation['log'])

        super().__init__()

    @property
    def acquirer(self):
        """
        Expõe o atribuito Adquirente que processará o Cartão de Crédito

        :return:
            `str`
        """
        return self.__soul['acquirer']

    @acquirer.setter
    def acquirer(self, value):
        """
        Define o Adquirente que processará o Cartão de Crédito

        :param value:
            `str`
        """
        assert value == 'CIELO', 'Adquirente não suportado: [{}]'.format(value)

        self.__soul['acquirer'] = value

    @property
    def validation(self) -> Validation:
        """

        :return:
        """
        return self.__validation_obj

    @property
    def authorization(self) -> Authorization:
        """

        :return:
        """
        return self.__authorization_obj

    @property
    def catch(self) -> Catch:
        """

        :return:
        """
        return self.__catch_obj

    @property
    def cancellation(self) -> Cancellation:
        """

        :return:
        """
        return self.__cancellation_obj


class PaymentInfo(object):
    """
    Informações do pagamento
    """

    def __init__(self, soul: dict):
        """
        Inicializa o objeto

        :param soul:
            Dicionário que representa as informações do pagamento
        """
        self.__credit_card_obj = None

        self.__soul = {
            'method': None,
            'credit_card': {
                'hash': None,
                'acquirer': 'CIELO',
                'validation': {
                    'valid': False,
                    'when': None,
                    'log': list()
                },
                'authorization': {
                    'authorized': False,
                    'when': None,
                    'log': list()
                },
                'catch': {
                    'captured': False,
                    'when': None,
                    'log': list()
                },
                'cancellation': {
                    'canceled': False,
                    'when': None,
                    'log': list()
                }
            }
        }
        self.__soul.update(soul)

        super().__init__()

    @property
    def method(self) -> str:
        """
        Expõe o atributo de Meio de Pagamento escolhido

        :return:
            `str`
        """
        return self.__soul['method']

    @method.setter
    def method(self, value: str):
        """
        Atribui o nome do Meio de Pagamento escolhido

        :param value:
            Nome do Meio de Pagamento escolhido
        """
        self.__soul['method'] = value

    @property
    def credit_card(self) -> CreditCardInfo:
        """
        Expõe o atribtuo referente às transações com o Cartão de Crédito

        :return:
            `CreditCardInfo`
        """
        if not self.__credit_card_obj:
            self.__credit_card_obj = CreditCardInfo(self.__soul['credit_card'])

        return self.__credit_card_obj

    @property
    def soul(self):
        """
        Retorna a representação em dicionário da Informações do Pagamento

        :return:
            `dict`
        """
        self.__soul.update({
            'credit_card': {
                'validation': {
                    'valid': self.credit_card.validation.valid,
                    'when': self.credit_card.validation.when,
                    'log': self.credit_card.validation.log
                },
                'authorization': {
                    'authorized': self.credit_card.authorization.authorized,
                    'when': self.credit_card.authorization.when,
                    'log': self.credit_card.authorization.log
                },
                'catch': {
                    'captured': self.credit_card.catch.captured,
                    'when': self.credit_card.catch.when,
                    'log': self.credit_card.catch.log
                },
                'cancellation': {
                    'canceled': self.credit_card.cancellation.canceled,
                    'when': self.credit_card.cancellation.when,
                    'log': self.credit_card.cancellation.log
                }
            }
        })
        return self.__soul
