# coding: utf-8

from requests import post

CHAVE_DA_API_DA_WEB = 'AIzaSyBI7uhs8Y877CGg5fRKpx8U8fM5jWahz_g'


class LinkShort(object):
    """

    """

    def __init__(self, link: str):
        """

        :param link:
        """
        self.__link = link
        super().__init__()

    def __call__(self):
        """

        :return:
        """
        response = post(
            'https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key={api_key}'.format(api_key=CHAVE_DA_API_DA_WEB),
            data={'longDynamicLink': 'https://mysofie.page.link/?link={to_redirect}'.format(to_redirect=self.__link)}
        )

        print(response.json())


if __name__ == '__main__':
    sender = LinkShort('https://mysofie.com/api/v1/pay/e4d0cf46-a241-4573-98db-49270c27b6ef')
    sender()
