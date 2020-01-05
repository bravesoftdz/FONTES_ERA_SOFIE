# coding: utf-8


from crud.sofier import SofierCRUD
from library.common.governance import DEVELOPER_SESSION
from library.common.paging_info import PagingInfo


class Sofier(object):
    """
    Classe ORM que representa um Sofier
    """

    class BankCheckingAccount(object):
        """

        """

        def __init__(self, soul: dict):
            """

            """
            self.__soul = soul
            super().__init__()

        def check(self):
            """

            :return:
            """
            for key in ('code', 'name', 'agency', 'account', 'account_digit'):
                if not self.__soul.get(key, None):
                    raise Exception('A conta bancária não foi definida ou contêm erros')

        @property
        def code(self):
            """

            :return:
            """
            if 'code' in self.__soul:
                return self.__soul['code']

        @property
        def name(self):
            """

            :return:
            """
            return self.__soul.get('name', '')

        @property
        def agency(self):
            """

            :return:
            """
            return self.__soul.get('agency', '')

        @property
        def account(self):
            """

            :return:
            """
            return self.__soul.get('account', '')

        @property
        def account_digit(self):
            """

            :return:
            """
            return self.__soul.get('account_digit', '')

    def __init__(self, sofier: str):
        """
        Inicializa o objeto

        :param sofier:
            ID do Sofier
        """
        self.__soul = SofierCRUD(PagingInfo(), DEVELOPER_SESSION).item(sofier)
        self.__bank_checking_account_obj = None
        super().__init__()

    @property
    def sofier(self) -> str:
        """
        Expõe o ID do Sofier

        :return:
            ID so Sofier
        """
        return self.__soul['sofier_id']

    @property
    def full_name(self) -> str:
        """
        Expõe o nome completo do Sofier

        :return:
            `str`
        """
        if self.__soul.get('full_name'):
            return self.__soul['full_name']
        else:
            return self.__soul.get('short_name', self.__soul['name'])

    @property
    def short_name(self) -> str:
        """
        Expõe o nome curto do Sofier

        :return:
            `str`
        """
        if 'short_name' in self.__soul:
            return self.__soul['short_name']
        else:
            return self.sofier

    @property
    def bank_checking_account(self) -> BankCheckingAccount:
        """

        :return:
        """
        if not self.__bank_checking_account_obj:
            return Sofier.BankCheckingAccount(self.__soul.get('bank_checking_account', dict()))

        return self.__bank_checking_account_obj

    @property
    def email(self) -> str:
        """

        :return:
        """
        return self.__soul.get('email', '')


if __name__ == '__main__':
    CPF = '32379386889'

    sofier = Sofier(CPF)
    print(sofier.sofier)
    print(sofier.full_name)
    print(sofier.short_name)
