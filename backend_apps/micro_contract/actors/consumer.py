# coding: utf-8

from datetime import datetime

from crud.consumer import ConsumerCRUD
from library.common.governance import DEVELOPER_SESSION
from library.common.paging_info import PagingInfo


class Consumer(object):
    """
    Classe ORM da classe de recurso Consumer
    """

    def __init__(self, consumer: str):
        """
        Inicializa o objeto

        :param consumer:
            Identificação do consumdiro
        """
        self.__soul = ConsumerCRUD(PagingInfo(), DEVELOPER_SESSION).item(consumer)

        super().__init__()

    @classmethod
    def exists(cls, consumer: str) -> bool:
        """
        Verifica a exisitência de um consimidor na base de dados

        :param consumer:
            ID do consumidor
        :return:
            `bool`
        """
        ConsumerCRUD(PagingInfo(), DEVELOPER_SESSION).exists(consumer, True)
        return True

    @property
    def consumer(self):
        """
        Expõe o ID do Consumidor

        :return:
            ID do Consumidor
        """
        return self.__soul['name']

    @property
    def email(self):
        """
        Expõe o atributo email do Consumidor

        :return:
            Email do Consumidor
        """
        return self.__soul['main_email']

    @property
    def phone(self):
        """
        Expõe o atributo telefone do Consumidor

        :return:
            Telefone do consumidor
        """
        return self.__soul['main_phone']

    @property
    def full_name(self):
        """

        :return:
        """
        return self.__soul['full_name']

    @property
    def to_care(self) -> str:
        """

        :return:
        """
        return self.__soul.get('to_care', '')

    @property
    def gender(self):
        """

        :return:
        """
        return self.__soul.get('gender', 'O')

    @property
    def kind_of_person(self):
        """

        :return:
        """
        return self.__soul['kind_of_person']

    @property
    def birthday(self) -> datetime:
        """

        :return:
        """
        return self.__soul['birthday']
