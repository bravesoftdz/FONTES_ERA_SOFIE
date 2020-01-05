# coding: utf-8


from crud.company import CompanyCRUD
from library.common.governance import DEVELOPER_SESSION
from library.common.paging_info import PagingInfo


class Company(object):
    """
    Representação da Em
    """

    def __init__(self, company: str):
        """
        Inicializa o objeto

        :param company:
            Nome da empresa
        """
        self.__soul = CompanyCRUD(PagingInfo(), DEVELOPER_SESSION).item(company)
        super().__init__()

    @property
    def company(self):
        """
        Expõe o nome da empresa

        :return:
            Nome da empresa
        """
        return self.__soul['name']

    @property
    def full_name(self):
        """

        :return:
        """
        return self.__soul['full_name']
