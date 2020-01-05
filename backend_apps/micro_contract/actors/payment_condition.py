# coding: utf-8


from crud.card import CardCRUD
from library.common.governance import DEVELOPER_SESSION
from library.common.paging_info import PagingInfo


class PaymentCondition(object):
    """
    Classe ORM que representa o método de pagamento escolhido
    """

    def __init__(self, card: str or None, payment_condition: str or None):
        """
        Inicializa o objeto

        :param card:
            ID do Card
        :param payment_condition:
            Nome do método de pagamento escolhido
        """
        self.__soul = None

        if card:
            self.__soul = CardCRUD(PagingInfo(fields=['payment_conditions.$']), DEVELOPER_SESSION).item(card, **{'payment_conditions.title': payment_condition})['payment_conditions'][0]

        super().__init__()

    @classmethod
    def from_soul(cls, soul: dict):
        """
        Monta uma instância desta classe à partir de um dicionário já pré existente

        :param soul:
            `dict`
        """
        buffer = PaymentCondition(None, None)
        buffer._PaymentCondition__soul = soul

        return buffer

    @property
    def soul(self) -> dict:
        """
        Expõe o dicionário que representa toda a informação

        :return:
            `dict`
        """
        return self.__soul

    @property
    def quotes(self) -> int:
        """
        Expõe a quantidade de parcelas

        :return:
            `int`
        """
        return self.__soul['quotes']['qtt']

    @property
    def quote_value(self) -> float:
        """
        Expõe o valor de cada parcela, quando aplicável

        :return:
            `float`
        """
        return self.__soul['quotes']['value']

    @property
    def price(self) -> float:
        """
        Expõe o valor a ser pago pelo consumidor

        :return:
            `float`
        """
        return self.__soul['price']

    @property
    def method(self) -> str:
        """
        Expõe o método de pagamento associado à esta condição de pagamento

        :return:
            `str`
        """
        return self.__soul['method']

    @property
    def reward(self) -> float:
        """
        Expõe o valor do prêmio ao Sofier

        :return:
            `str`
        """
        return self.__soul['reward']
