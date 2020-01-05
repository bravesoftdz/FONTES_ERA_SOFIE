# coding: utf-8

"""
Módulo responsável por criar as configurações iniciais da plataforma MySofie
"""

raise Exception('TEM CERTEZA ABSOLUTA QUE QUER FAZER ISSO??????')

from os import path

from crud.company import CompanyCRUD
from crud.user import UserCRUD
from library.common.governance import DEVELOPER_SESSION
from library.crud.crud_base import PagingInfo
from library.storage.config import ConfigStorage
from library.storage.caching import CachingStorage
from library.storage.session import SessionStorage

CachingStorage().storage.flushall()

SessionStorage().storage.flushall()

INDEX_COLLECTIONS = {
    'address': [('name', 1)],
    'address_association': [('address', 1), ('user', 1)],
    'card': [('name', 1)],
    'card_know': [('sofier', 1), ('card', 1)],
    'company': [('name', 1)],
    'consumer': [('name', 1)],
    'ledger': [('name', 1)],
    'micro_contract': [('name', 1)],
    'sofier': [('sofier_id', 1)],
    'training': [('name', 1)],
    'transaction': [('transaction', 1)],
    'user': [('name', 1)],
    'lead': [('name', 1)],
}

config = ConfigStorage().config
for collection, index in INDEX_COLLECTIONS.items():
    config[collection].drop()
    config[collection].create_index(index, unique=True)

user_crud = UserCRUD(PagingInfo(), DEVELOPER_SESSION)
user_crud.create(
    'jmarioguedes@gmail.com',
    {
        'name': 'jmarioguedes@gmail.com',
        'full_name': 'José Mario Silva Guedes',
        'short_name': 'Mario Guedes',
        'cpf': '19678335832',
        'level': 'PLATFORM',
        'company': None,
        'password': 'MTIzNDU2Nzg='
    }
)

user_crud.create(
    'thiago.filadelfo@mysofie.com',
    {
        'name': 'thiago.filadelfo@mysofie.com',
        'full_name': 'Thiago Ribeiro Filadelfo',
        'short_name': 'Thiago',
        'cpf': '32379386889',
        'level': 'PLATFORM',
        'company': None,
        'password': 'MTIzNDU2Nzg='
    }
)

company_crud = CompanyCRUD(PagingInfo(), DEVELOPER_SESSION)
company_crud.create(
    'caras',
    {
        'name': 'caras',
        'full_name': 'Editora Caras',
        'cnpj': '56324114000141',
        'active': True,
        'card_bookmark_color': '#ff0002'
    }
)

company_crud.create(
    'flor_de_sal',
    {
        'name': 'flor_de_sal',
        'full_name': 'Flor de Sal',
        'cnpj': '45346647000108',  #: CNPJ FICTÍCIO
        'active': True,
        'card_bookmark_color': '#610B0B'
    }
)

caminho = path.join('.', '..')
caminho = path.join(caminho, 'resources', 'logo_caras.png')

with open(caminho, 'rb') as arquivo:
    company_crud.define_image('caras', arquivo.read())

caminho = path.join('.', '..')
caminho = path.join(caminho, 'resources', 'logo_flor_de_sal.jpg')

with open(caminho, 'rb') as arquivo:
    company_crud.define_image('flor_de_sal', arquivo.read())


user_crud.create(
    'exemplo@caras.com.br',
    {
        'full_name': 'Usuário Exemplo',
        'short_name': 'Exemplo',
        'cpf': '19678335832',
        'level': 'COMPANY',
        'company': 'caras',
        'password': 'MTIzNDU2Nzg='
    }
)
