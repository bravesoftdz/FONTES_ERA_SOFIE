from datetime import datetime
from locale import setlocale, LC_ALL

from crud.card import CardCRUD
from library.common.governance import DEVELOPER_SESSION
from library.crud.crud_base import PagingInfo

setlocale(LC_ALL, 'pt_BR.UTF-8')

crud = CardCRUD(PagingInfo(), DEVELOPER_SESSION)


def convert2float(value: str) -> float:
    """

    :param value:
    :return:
    """
    new_value = value.replace('.', '').replace(',', '.').replace('R$ ', '').strip()
    return float(new_value)


buffer = {
    'company': 'flor_de_sal',
    'expertise': 'SALE',
    'title': {
        'title': 'Card de Teste',
        'sub_title': 'Teste'
    },
    'description_on_invoice': 'CardTeste',
    'bookmarks': {
        'card': {
            'display': True,
            'row_1': '1',
            'row_2': 'Unidade',
            'row_3': ''
        },
        'detail_1': {
            'display': False,
            'row_1': '',
            'row_2': '',
            'row_3': ''
        },
        'detail_2': {
            'display': False,
            'row_1': '',
            'row_2': '',
            'row_3': ''
        },
        'detail_3': {
            'display': False,
            'row_1': None,
            'row_2': None,
            'row_3': None
        }
    },
    'description': '<strong>Card de teste</strong>',
    'training': None,
    'micro_contract': 'caras_contract',
    'validity': {
        'start': datetime.utcnow(),
        'end': datetime.utcnow()

    },
    'payment_conditions': [{
        'title': 'À vista!',
        'method': 'CREDIT_CARD',
        'price': 1.01,
        'reward': 1,
        'fee': 0.01,
        'points': 0,
        'quotes': {
            'qtt': 1,
            'value': 1.01,
            'with_rate': False
        },
        'days_for_reward': 7
    }],
    'reference_codes': {
        'reference_1': None,
        'reference_2': None
    }
}

inserted = crud.create('', buffer, force_projection=True)

with open('brigadeiro.png', 'rb') as arquivo:
    cover = arquivo.read()

crud.define_image(inserted['name'], cover)
