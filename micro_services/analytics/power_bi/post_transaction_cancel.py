# coding: utf-8

from micro_services.analytics.power_bi.powerbi_base import PowerBIBase
from micro_services.analytics.power_bi.get_token import PowerBIAuth
from library.storage.config import ConfigStorage


class PowerBICards(PowerBIBase):
    EVENTS = ['transaction_cancel']

    def __init__(self):
        super().__init__('b925367f-28c6-4534-aebc-9c10e47050cc', '8d1f965b-31d4-4c21-9f80-698462709068', 'Transactions')

    def __call__(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        # TODO: Rever a Linha abaixo revendo um CRUD da Transição
        transaction = ConfigStorage().config['transaction'].find_one({'transaction': kwargs['data']['transaction']},
                                                                     {'_id': 0})

        data = {
            'rows':
                [{'transaction_id': kwargs['data']['transaction'],
                  'when': kwargs['data']['timestamp'].strftime('%m/%d/%Y'),
                  'status': 'CANCELADO',
                  'success': transaction['status']['success'],
                  'reason': transaction['status']['reason'],
                  'payment_link': transaction['payment_link'].get('media', 'Sem Midia')
                  }]}

        self.execute_post(data)

        return True


if __name__ == '__main__':
    power_auth = PowerBIAuth()
    print('TOKEN POWER BI', power_auth.token)

    from backend_apps.events.transaction import TransactionCancelEvent

    conteudo = TransactionCancelEvent(transaction='d9cf712e-dc4a-11e8-9660-0242ac110002').to_dict()

    print(conteudo)

    powerbi_post = PowerBICards()
    powerbi_post(**conteudo)
