# coding: utf-8

"""
Aglutina as exceções relacioandas ao processo de transação
"""

from http import HTTPStatus

from library.common.exception import MySofieException


class CardAlreadyDefined(MySofieException):
    """
    Indica que a a Transação já possui um Card associado
    """

    status_http = HTTPStatus.BAD_REQUEST.value

    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__('A Transação já está associado a um Card')


class SofierAlreadyDefined(MySofieException):
    """
    Indica que a a Transação já possui um Sofier associado
    """

    status_http = HTTPStatus.BAD_REQUEST.value

    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__('A Transação já está associado a um Sofier')


class ConsumirAlreadyDefined(MySofieException):
    """
    Indica que a a Transação já possui um Consumidor associado
    """

    status_http = HTTPStatus.BAD_REQUEST.value

    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__('A Transação já está associado a um Consumidor')


class CardNotDefined(MySofieException):
    """
    Indica que não foi definido um Card
    """

    status_http = HTTPStatus.BAD_REQUEST.value

    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__('Não foi definido um Card válido')


class PaymentNotApplicable(MySofieException):
    """
    Indica que o Card não é sujeito à um pagamento por parte do Consumidor
    """

    status_http = HTTPStatus.BAD_REQUEST.value

    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__('O Card não é passível de pagamento por parte do Consumidor')


class PaymentMethodNotSupported(MySofieException):
    """
    Indica que o método de pagamento não é suportado
    """

    status_http = HTTPStatus.BAD_REQUEST.value

    def __init__(self, payment_method: str):
        """
        Inicializa o objeto

        :param payment_method:
             Nome do método de pagamento
        """
        self.__payment_method = payment_method
        super().__init__('O método de pagamento [{}] não é suportado'.format(self.__payment_method))

    @property
    def payment_method(self) -> str:
        """

        :return:
        """
        return self.__payment_method


class PaymentConditionNotSupported(MySofieException):
    """
    Indica que a Condição de Pagamento não é reconhecida pelo Card
    """

    status_http = HTTPStatus.BAD_REQUEST.value

    def __init__(self, payment_condition: str):
        """
        Inicializa o objeto

        :param payment_condition:
            Nome da condição de pagamento
        """
        self.__payment_condition = payment_condition
        super().__init__('A condição de pagamento [{}] não é reconhecida pelo Card'.format(payment_condition))

    @property
    def payment_condition(self) -> str:
        """
        Expõe o atributo Condição de Pagamento

        :return:
            `str`
        """
        return self.__payment_condition


class TransactionClosed(MySofieException):
    """
    Indica que a transação esta em um estado em que não aceita mais coleta de dados
    """

    status_http = HTTPStatus.BAD_REQUEST.value

    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__('A transação não aceita mais coleta de dados')


class DoubleSpend(MySofieException):
    """
    Indica que o pagamento já foi efetuado
    """

    status_http = HTTPStatus.BAD_REQUEST.value

    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__('O pagamento já foi efetuado')


class TransactionCanceled(MySofieException):
    """
    Indica que a transação em questão foi cancelada
    """

    status_http = HTTPStatus.BAD_REQUEST.value

    def __init__(self, transaction: str):
        """
        Inicializa o objeto
        """
        self.__transaction = transaction
        super().__init__('A transação [{}] foi cancelada'.format(transaction))

    def transaction(self):
        """

        :return:
        """
        return self.__transaction


class TransactionFinished(MySofieException):
    """

    """

    status_http = HTTPStatus.BAD_REQUEST.value

    def __init__(self, transaction: str):
        """

        """
        self.__transaction = transaction
        super().__init__('A transação [{}] já foi finalizada.'.format(transaction))

    def transaction(self):
        """

        :return:
        """
        return self.__transaction


class TransactionNotFound(MySofieException):
    """
    Indica que a transação não existe no banco de dados ou não foi definida
    """

    status_http = HTTPStatus.BAD_REQUEST.value

    def __init__(self, transaction: str):
        """
        Inicializa o objeto
        """
        self.__transaction = transaction
        super().__init__('A transação não foi localizada no banco de dados: [{}]'.format(transaction))

    @property
    def transaction(self):
        """

        :return:
        """
        return self.__transaction


class PaymentLinkExpired(MySofieException):
    """

    """

    status_http = HTTPStatus.BAD_REQUEST.value

    def __init__(self, transaction: str):
        """
        Inicializa o objeto
        """
        self.__transaction = transaction
        super().__init__('O link de pagamento da transação [{}] expirou'.format(transaction))

    @property
    def transaction(self):
        """

        :return:
        """
        return self.__transaction


class PaymentInProgress(MySofieException):
    """
    Indica que o pagamento está em andamento
    """

    status_http = HTTPStatus.BAD_REQUEST.value

    def __init__(self, transaction: str):
        """
        Inicializa o objeto
        """
        self.__transaction = transaction
        super().__init__('O pagamento da transação [{}] está em andamento'.format(transaction))

    @property
    def transaction(self):
        """

        :return:
        """
        return self.__transaction
