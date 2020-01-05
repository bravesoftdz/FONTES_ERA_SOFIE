# coding: utf-8

from library.common.governance import DEVELOPER_SESSION
from library.common.paging_info import PagingInfo
from micro_services.analytics.power_bi import PowerBIBase
from micro_services.analytics.power_bi.get_token import PowerBIAuth
from crud.card import CardCRUD


class PowerBICards(PowerBIBase):
    EVENTS = ['transaction_create']

    def __init__(self):
        super().__init__('b925367f-28c6-4534-aebc-9c10e47050cc', '8d1f965b-31d4-4c21-9f80-698462709068', 'Cards')

    def __call__(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        card = CardCRUD(PagingInfo(), DEVELOPER_SESSION).item(kwargs['data']['card'], True)

        data = {
            'rows':
                [{'transaction_id': kwargs['data']['transaction'],
                  'card_id': kwargs['data']['card'],
                  'card_title': card['title']['title'],
                  'card_company': card['company'],
                  'card_booksmark': card['bookmarks']['card']['row_1']
                                    + ' '
                                    + card['bookmarks']['card']['row_2']
                                    + ' '
                                    + card['bookmarks']['card']['row_3']
                  }]}

        self.execute_post(data)

        return True


if __name__ == '__main__':
    power_auth = PowerBIAuth()
    print('TOKEN POWER BI', power_auth.token)

    powerbi_post = PowerBICards()
    powerbi_post(
        **{
            'type': 'transaction_create',
            'data': {'sofier': '41099083885',
                     'card': '893b0627-cc99-43b4-ad4d-7e1414f9e25b',
                     'transaction': 'c'
                     }
        }
    )
