# coding: utf-8

"""
Centralização do ponto de acesso ao storage Relation da plataforma MySofie

A fim de centralizar o ponto de manutenção do acesso ao storage Relation da plataforma MySofie foi
criado este módulo com uma classe singleton.

Para que o mecanismo funcione adequadamente é necessário passar o parâmetro --relation com a URI de
acesso ao banco de dados:

e.g. programa -c  bolt://localhost:7687

A instância do banco pode ser acessado pelo atributo **storage**
"""

from argparse import ArgumentParser

from neo4j.v1 import GraphDatabase, Driver, basic_auth

from library.common.exception import MySofieException

params = ArgumentParser(
    prog='RelationStorage',
    usage='Storage Relation da plataforma MySofie',
    description='Provê ponto centralizado de acesso ao Neo4J do Sofie'
)
params.add_argument('-r', '--relation', help='URI de acesso ao storage Relation', type=str, required=True)
ARGS = params.parse_known_args()[0]


class RelationStorage(object):
    """
    Classe singleton que acessa o MongoDB responsável pela configuração do ecossistema MySofie
    """

    __initiated = False
    __storage_point = None

    def __new__(cls, *args, **kwargs):
        """
        Abordagem para tornar a classe singleton

        http://aprenda-python.blogspot.com.br/2012/11/singleton-simples-em-python.html
        """
        if not hasattr(cls, '_instance'):
            cls._instance = super(RelationStorage, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        """
        Inicialização da instância
        """
        if not RelationStorage.__initiated:
            RelationStorage.__initiated = True
            RelationStorage.__storage_point = GraphDatabase.driver(ARGS.relation, auth=basic_auth('neo4j', 'sofie@admin'))

            super().__init__()

    @property
    def storage(self) -> Driver:
        """
        Ponto de acesso único ao storage Config

        :return:
            Instância do client ao storage
        """
        if not RelationStorage.__initiated:
            raise MySofieException('ConfigStorage não inicializado')

        return RelationStorage.__storage_point

    def run(self, cypher: str, parameters: dict or None = None, **kwargs):
        """
        Executa instruções Cypher sob uma sessão, facilitando a utilização

        :param cypher:
            Instruções Cypher
        :param parameters:
            Dicionário com os parâmetros da consulta
        """
        with self.__storage_point.session() as session:
            return session.run(cypher, parameters, **kwargs)
