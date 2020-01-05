# coding: utf-8


from crud.card import CardCRUD
from library.common.governance import DEVELOPER_SESSION
from library.common.paging_info import PagingInfo


class ReferenceCodes(object):
    """

    """

    def __init__(self, soul: dict):
        """

        :param soul:
        """
        self.__soul = soul
        super().__init__()

    def __getitem__(self, item):
        """

        :param item:
        :return:
        """
        key = 'reference_{}'.format(item)
        return self.__soul.get(key, '')


class Card(object):
    """
    Classe ORM que representa um Card
    """

    def __init__(self, card: str):
        """
        Inicializa o objeto

        :param card:
            Código Card
        """
        self.__soul = CardCRUD(PagingInfo(), DEVELOPER_SESSION).item(card, consider_archiveds=True)
        self.__reference_codes_obj = None
        super().__init__()

    @property
    def card(self):
        """
        Expõe o nome do Card

        :return:
            Nome do Card
        """
        return self.__soul['name']

    @property
    def expertise(self) -> str:
        """
        Expõe o _expertise_ exigido pelo Card

        :return:
            Expertise do Card
        """
        return self.__soul['expertise']

    @property
    def company(self):
        """
        Expõe a Empresa à qual pertence o Card

        :return:
            Nome da Empresa
        """
        return self.__soul['company']

    @property
    def title(self):
        """
        Expõe o Título principal do Card

        :return:
            Título principal do Card
        """
        return self.__soul['title']['title']

    @property
    def sub_title(self):
        """

        :return:
        """
        return self.__soul['title']['sub_title']

    @property
    def formatted_title(self):
        """

        :return:
        """
        return '{} - {}'.format(self.__soul['title']['title'], self.__soul['title']['sub_title'])

    @property
    def reference_codes(self) -> ReferenceCodes:
        """
        Expõe os códdigos de refeência em relação à emppresa para efeitos de integração

        :return:
            `ReferenceCodes`
        """
        if not self.__reference_codes_obj:
            if 'reference_codes' in self.__soul:
                self.__reference_codes_obj = ReferenceCodes(self.__soul['reference_codes'])
            else:
                self.__reference_codes_obj = ReferenceCodes(dict())

        return self.__reference_codes_obj

    @property
    def description_on_invoice(self) -> str:
        """

        :return:
        """
        return self.__soul.get('description_on_invoice', '')

    @property
    def description(self) -> str:
        """

        :return:
        """
        return self.__soul.get('description', '')

    @property
    def data_collect_flow(self) -> list:
        """

        :return:
        """
        return self.__soul.get('data_collect_flow', list())

    @property
    def soul(self):
        """

        :return:
        """
        return self.__soul
