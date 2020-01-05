# coding: utf-8


class GeoLocation(object):
    """

    """

    def __init__(self, soul: dict):
        """

        """
        self.__soul = soul
        super().__init__()

    @property
    def soul(self) -> dict:
        """

        :return:
        """
        return self.__soul

    @soul.setter
    def soul(self, value: dict):
        """

        :param value:
        :return:
        """
        self.__soul = value

    @property
    def altitude(self):
        """

        :return:
        """
        return self.__soul.get('altitude', '')

    @altitude.setter
    def altitude(self, value: str):
        """

        :param value:
        :return:
        """
        self.__soul['altitude'] = value

    @property
    def latitude(self) -> str:
        """

        :return:
        """
        return self.__soul.get('latitude', '')

    @latitude.setter
    def latitude(self, value: str):
        """

        :param value:
        :return:
        """
        self.__soul['latitude'] = value

    @property
    def accuracy(self) -> str:
        """

        :return:
        """
        return self.__soul.get('accuracy', '')

    @accuracy.setter
    def accuracy(self, value: str):
        """

        :param value:
        :return:
        """
        self.__soul['accuracy'] = value

    @property
    def longitude(self) -> str:
        """

        :return:
        """
        return self.__soul.get('longitude', '')

    @longitude.setter
    def longitude(self, value: str):
        """

        :param value:
        :return:
        """
        self.__soul['longitude'] = value
