# coding: utf-8

"""

"""


class FeedbackConsumer(object):
    """

    """

    def __init__(self, soul):
        """

        :param soul:
        """
        self.__soul = soul
        super().__init__()

    @property
    def feedback_done(self) -> bool:
        """

        :return:
        """
        return self.when is not None

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
    def when(self):
        """

        :return:
        """
        return self.__soul.get('when')

    @when.setter
    def when(self, value):
        """

        :param value:
        :return:
        """
        self.__soul['when'] = value

    @property
    def nps(self):
        """

        :return:
        """
        return self.__soul.get('nps')

    @nps.setter
    def nps(self, value):
        """

        :param value:
        :return:
        """
        self.__soul['nps'] = value

    @property
    def comment(self):
        """

        :return:
        """
        return self.__soul.get('comment')

    @comment.setter
    def comment(self, value):
        """

        :param value:
        :return:
        """
        self.__soul['comment'] = value
