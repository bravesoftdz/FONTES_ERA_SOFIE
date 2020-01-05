# coding: utf-8

"""
CRUD relacionado à Classe de Recurso: `Consumer`
"""

from http import HTTPStatus

from library.common.exception import MySofieException
from library.common.governance import LEVEL_PLATFORM, LEVEL_DEVELOPER, LEVEL_COMPANY, LEVEL_SOFIER, LEVEL_CONSUMER, LEVEL_APP_MYSOFIE
from library.common.miscellaneous import datetime2string, cnpj_is_valid, cpf_is_valid
from library.crud.crud_base import CRUDBase, AllowedLevels, InvalidDocument
from library.storage.caching import apply_caching
from library.storage.relation import RelationStorage
from scheme.consumer import SCHEME_CONSUMER


class ConsumerNotVisible(MySofieException):
    """
    Indica que o usuário solicitante não tem acesso aos dados de um determiando consumidor ou este não
    existe em nossa base
    """

    status_http = HTTPStatus.GONE.value

    def __init__(self, consumer: str):
        """
        Inicia o objeto

        :param consumer:
            CPF que representa o consumidor
        """
        self.__consumer = consumer

    def __str__(self):
        """
        Formatação da mensagem de erro

        :return:
        """
        return 'O consumidor [{}] não é visível ao usuário solicitante ou não existe'.format(self.__consumer)

    @property
    def consumer(self):
        """
        Expõe o atributo `consumer` que é representado pelo CPF do consumidor

        :return:
            CPF do consumidor
        """
        return self.__consumer


class ConsumerCRUD(CRUDBase):
    """
    CRUD referente à Classe de Recurso `consumer`
    """

    resource_class = 'consumer'

    scheme = SCHEME_CONSUMER

    levels_permissions = AllowedLevels(
        listing=[LEVEL_PLATFORM, LEVEL_COMPANY, LEVEL_DEVELOPER, LEVEL_SOFIER],
        item=[LEVEL_PLATFORM, LEVEL_COMPANY, LEVEL_DEVELOPER, LEVEL_SOFIER, LEVEL_APP_MYSOFIE],
        create=[LEVEL_SOFIER, LEVEL_DEVELOPER, LEVEL_APP_MYSOFIE],
        modify=[LEVEL_PLATFORM, LEVEL_SOFIER, LEVEL_DEVELOPER, LEVEL_APP_MYSOFIE],
        archive=[]
    )

    CYPHER_INSERT = """
    MERGE (c:CONSUMER {name: {consumer}})
    WITH c
    MATCH (s:SOFIER {name: {sofier}})
    MERGE (s)-[:REGISTERED{date:{when}}]->(c)
    """

    CYPHER_VERIFY_BY_COMPANY = """
    MATCH cursor=(:CONSUMER{name:{consumer}})-[:ACQUIRED]->(:CARD)<-[:OFFER]-(:COMPANY{name:{company}})
    RETURN count(cursor) AS total
    """

    def before_document_is_valid(self, document: dict) -> dict:
        """

        :param document:
        :return:
        """
        if document['kind_of_person'] == 'F':
            if not cpf_is_valid(document['name']):
                raise InvalidDocument('CPF')
        elif document['kind_of_person'] == 'J':
            if not cnpj_is_valid(document['name']):
                raise InvalidDocument('CNPJ')
        else:
            raise InvalidDocument('Natureza Jurídica')

        return document

    def build_relationship(self, document: dict):
        """
        Método a ser sobrescrito nas classes descendentes com o propósito de refazer os relacionamentos no Neo4J

        :param document:
            Documento que engatilhou o método
        """
        RelationStorage().run(
            ConsumerCRUD.CYPHER_INSERT,
            consumer=document['name'],
            sofier=document['__created__']['who']['user'],
            when=datetime2string(document['__created__']['when'])
        )

    def get_keys_to_clear_cache(self, document: dict) -> list:
        """
        Método a ser sobrescrito nas classes descendentes com o propósito de devolver a lista de chaves para limpeza de
        cache

        :param document:
            Documento que engatilhou a limpeza do cache
        """
        return [
            'MYSOFIE:CACHE:CONSUMER:{}:DATA#'.format(document['name'])
        ]

    @apply_caching('MYSOFIE:CACHE:CONSUMER:{1}:DATA#', 60 * 10)
    def item(self, name: str, **kwargs):
        """

        :param name:
        :param kwargs:
        :return:
        """
        if self.session.level == LEVEL_COMPANY:
            cursor = list(RelationStorage().run(ConsumerCRUD.CYPHER_VERIFY_BY_COMPANY, consumer=name, company=self.session.company))
            if cursor[0]['total'] == 0:
                raise ConsumerNotVisible(name)

        elif self.session.level == LEVEL_CONSUMER:
            if self.session.user != name:
                raise ConsumerNotVisible(name)

        return super().item(name, **kwargs)

    def listing(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        if self.session.level == LEVEL_COMPANY:
            raise Exception('Operação ainda não suportada')

        elif self.session.level == LEVEL_SOFIER:
            raise Exception('Operação ainda não suportada')

        elif self.session.level == LEVEL_CONSUMER:
            kwargs['name'] = {'$in': [self.session.user]}

        return super().listing(**kwargs)

    def modify(self, name: str, document: dict):
        """

        :param name:
        :param document:
        """
        super().modify(name, document)
