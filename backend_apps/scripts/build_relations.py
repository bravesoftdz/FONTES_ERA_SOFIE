# coding: utf-8

"""
Script responsável por refazer o Neo4J com todos os relacionamentos e regras conforme
os novos entendimentos na jornada da construção do MySofie
"""

from crud.address import AddressCRUD, AddressAssociationCRUD
from crud.card import CardCRUD
from crud.company import CompanyCRUD
from crud.consumer import ConsumerCRUD
from crud.sofier import SofierCRUD
from crud.know import CardKnowCRUD
from crud.training import TrainingCRUD
from crud.user import UserCRUD
from library.common.governance import DEVELOPER_SESSION
from library.crud.crud_base import PagingInfo
from micro_contract.transaction import Transaction
from library.storage.relation import RelationStorage
from library.storage.config import ConfigStorage

NEO4J = RelationStorage()

NEO4J.run('MATCH (N) DETACH DELETE N')

NEO4J.run('CREATE CONSTRAINT ON (c:COMPANY) ASSERT c.name IS UNIQUE')
NEO4J.run('CREATE CONSTRAINT ON (s:SOFIER) ASSERT s.name IS UNIQUE')
NEO4J.run('CREATE CONSTRAINT ON (u:USER) ASSERT u.name IS UNIQUE')
NEO4J.run('CREATE CONSTRAINT ON (c:CARD) ASSERT c.name IS UNIQUE')
NEO4J.run('CREATE CONSTRAINT ON (t:TRAINING) ASSERT t.name IS UNIQUE')
NEO4J.run('CREATE CONSTRAINT ON (c:CONSUMER) ASSERT c.name IS UNIQUE')
NEO4J.run('CREATE CONSTRAINT ON (a:ADDRESS) ASSERT a.name IS UNIQUE')
NEO4J.run('CREATE CONSTRAINT ON (t:TRANSACTION) ASSERT t.name IS UNIQUE')

for ressource_class in (CompanyCRUD, TrainingCRUD, CardCRUD, SofierCRUD, UserCRUD, CardKnowCRUD, ConsumerCRUD, AddressCRUD, AddressAssociationCRUD):
    handler = ressource_class(PagingInfo(), DEVELOPER_SESSION)
    for item in handler.listing()['data']:
        handler.build_relationship(item)

for doc in ConfigStorage().config['transaction'].find():
    Transaction(doc['transaction']).create_relations()
