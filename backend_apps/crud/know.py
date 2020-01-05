# coding: utf-8

"""

"""

from library.crud.crud_base import CRUDBase
from library.storage.relation import RelationStorage
from scheme.consumer import SCHEME_CARD_KNOW


class CardKnowCRUD(CRUDBase):
    """

    """

    resource_class = 'card_know'

    scheme = SCHEME_CARD_KNOW

    CYPHER_SET_KNOW = """
    MATCH (s:SOFIER {name: {sofier}})
    MATCH (c:CARD {name: {card}})
    MERGE (s)-[:KNOW]->(c)    
    """

    def build_relationship(self, document: dict):
        """

        :param document:
            Documento que engatilhou o método
        """
        RelationStorage().run(CardKnowCRUD.CYPHER_SET_KNOW, sofier=document['sofier'], card=document['card'])

    def register_card_know(self, sofier: str, card: str):
        """

        :param sofier:
        :param card:
        :return:
        """
        document = {'sofier': sofier, 'card': card, 'date_time': None}

        self.collection.insert_one(document)
        self.build_relationship(document)
