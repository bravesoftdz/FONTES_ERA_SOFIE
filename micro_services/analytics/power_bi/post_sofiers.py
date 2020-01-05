# coding: utf-8

from library.common.governance import DEVELOPER_SESSION
from library.common.paging_info import PagingInfo
from micro_services.analytics.power_bi import PowerBIBase
from micro_services.analytics.power_bi.get_token import PowerBIAuth
from crud.sofier import SofierCRUD


class PowerBISofiers(PowerBIBase):

    EVENTS = ['transaction_create']

    def __init__(self):
        super().__init__('b925367f-28c6-4534-aebc-9c10e47050cc', '8d1f965b-31d4-4c21-9f80-698462709068', 'Sofiers')

    def __call__(self, **kwargs):
        """

        :param token:
        :param transaction_id:
        :param sofier_id:
        :param sofier_short_name:
        :param sofier_birthday:
        :return:
        """

        sofier = SofierCRUD(PagingInfo(), DEVELOPER_SESSION).item(kwargs['data']['sofier'], True)

        data = {
            'rows':
                [{'transaction_id': kwargs['data']['transaction'],
                  'sofier_id': kwargs['data']['sofier'],
                  'sofier_short_name': sofier['short_name'],
                  'sofier_birthday': sofier['birthday'].strftime('%d/%m/%Y')
                  }]}

        self.execute_post(data)

        return True


if __name__ == '__main__':
    power_auth = PowerBIAuth()
    print('TOKEN POWER BI', power_auth.token)

    powerbi_post = PowerBISofiers()
    powerbi_post(
        **{
            'type': 'transaction_create',
            'data': {'sofier': '41099083885',
                     'card': '893b0627-cc99-43b4-ad4d-7e1414f9e25b',
                     'transaction': 'c'
                     }
        }
    )
