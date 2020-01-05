# coding: utf-8


from crud.address import AddressCRUD
from library.common.governance import DEVELOPER_SESSION
from library.common.paging_info import PagingInfo


class Address(object):
    """

    """

    def __init__(self, address: str):
        """

        :param address:
        """
        self.__soul = AddressCRUD(PagingInfo(), DEVELOPER_SESSION).item(address)
        super().__init__()

    @property
    def address(self):
        """

        :return:
        """
        return self.__soul['name']

    @property
    def zipcode(self):
        """

        :return:
        """
        return self.__soul['address']['zip_code']

    @property
    def type(self) -> str:
        """
        Expõe o atributo Tipo do Logradouro, e.g. Rua

        :return:
            `str`
        """
        return self.__soul['address']['type']

    @property
    def full_name(self):
        """

        :return:
        """
        return self.__soul['address']['full_name']

    @property
    def number(self):
        """

        :return:
        """
        return self.__soul['address']['number']

    @property
    def complement(self):
        """

        :return:
        """
        return self.__soul['address']['complement']

    @property
    def reference(self):
        """

        :return:
        """
        return self.__soul['address']['reference']

    @property
    def district(self):
        """

        :return:
        """
        return self.__soul['address']['district']

    @property
    def city(self):
        """

        :return:
        """
        return self.__soul['address']['city']

    @property
    def state(self):
        """

        :return:
        """
        return self.__soul['address']['state']

    @property
    def country(self):
        """

        :return:
        """
        return self.__soul['address']['country']

    @property
    def formated_address(self):
        """

        :return:
        """
        buffer = '{type} {full_name}, {number}, {complement} {district}, {city} - CEP: {cep_1}-{cep_2}'.format(
            type=self.type,
            full_name=self.full_name,
            number=self.number,
            complement=self.complement,
            district=self.district,
            city=self.city,
            cep_1=self.zipcode[:5],
            cep_2=self.zipcode[5:],
        )

        if self.complement:
            buffer = buffer.format(complement=self.complement + ',')

        return buffer
