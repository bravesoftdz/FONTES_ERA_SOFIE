# coding: utf-8

from datetime import datetime


class FraudPrevention(object):
    """

    """

    def __init__(self, soul: dict):
        """

        :param soul:
        """
        self.__soul = {
            'vendor': None,
            'approved': None,
            'when': None,
            'log': list()
        }

        self.__soul.update(soul)

        super().__init__()

    @property
    def soul(self):
        """

        :return:
        """
        return self.__soul

    @property
    def vendor(self) -> str:
        """

        :return:
        """
        return self.__soul.get('vendor', '')

    @vendor.setter
    def vendor(self, value: str):
        """

        :param value:
        :return:
        """
        self.__soul['vendor'] = value

    @property
    def approved(self) -> bool:
        """

        :return:
        """
        return self.__soul.get('approved', False)

    @approved.setter
    def approved(self, value: bool):
        """

        :return:
        """
        self.__soul['approved'] = value

    @property
    def when(self) -> datetime:
        """

        :return:
        """
        return self.__soul.get('when')

    @when.setter
    def when(self, value: datetime):
        """

        :param value:
        :return:
        """
        self.__soul['when'] = value

    @property
    def log(self) -> list:
        """

        :return:
        """
        return self.__soul['log']
