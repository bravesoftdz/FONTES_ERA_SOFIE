# coding: utf-8

"""
05/02/2019

Script para alinhar os novos campos obrigatórios da classe de recurso Sofier onde a chave deixa de ser CPF e passa a ser SOFIER_ID
que é um uuid1
"""

from uuid import uuid1

from library.storage.config import ConfigStorage

coll_sofie = ConfigStorage().config['sofier']

for item in coll_sofie.find({'sofier_id': {'$exists': False}}, {'_id': 1}):
    coll_sofie.update_one(item, {'$set': {'sofier_id': str(uuid1())}})

# GERAR DICIONÁRIO {CPF: SOFIER_ID}
SOFIERS = dict()
for sofier in coll_sofie.find():
    SOFIERS[sofier['name']] = sofier['sofier_id']

# [collection name , field , criteria]
INSTRUCTIONS = [
    ['address', '__created__.who.user'],
    ['address_association', '__created__.who.user'],
    ['consumer', '__created__.who.user'],
    ['ledger', 'part.id'],
    ['policies_accept', '__created__.who.user'],
    ['transaction', 'actors.sofier']
]


def get_value(dict_target: dict, dot_field: str):
    """

    :param dict_target:
    :param dot_field:
    :return:
    """
    fields = dot_field.split('.')

    buffer = dict_target.copy()
    for sub_field in fields:
        buffer = buffer.get(sub_field)

    return buffer


for collection, field in INSTRUCTIONS:
    coll_target = ConfigStorage().config[collection]
    for each in coll_target.find(projection={'_id': 1, field: 1}):
        print(collection, field, each['_id'])
        sofier_id = SOFIERS.get(get_value(each, field), None)
        if sofier_id:
            coll_target.update_one({'_id': each['_id']}, {'$set': {field: sofier_id}})
