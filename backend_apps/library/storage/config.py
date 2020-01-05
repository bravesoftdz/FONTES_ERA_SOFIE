# coding: utf-8

"""
Centralização do ponto de acesso ao storage Config da plataforma MySofie

A fim de centralizar o ponto de manutenção do acesso ao storage Config da plataforma MySofie foi
criado este módulo com uma classe singleton.

A ideia é suportar qualquer vendor mas atualmente, e por um bom tempo, só será suportado o MongoDB.

Para que o mecanismo funcione adequadamente é necessário passar o parâmetro --config com a URI de 
acesso ao banco de dados:

e.g. programa -c  mongodb://localhost:27017 

A instância do banco pode ser acessado pelo atributo **storage**
"""

from argparse import ArgumentParser
from platform import system

from pymongo import MongoClient
from pymongo.database import Database

from library.common.exception import MySofieException

params = ArgumentParser(
    prog='ConfigStorage',
    usage='Storage Config da plataforma MySofie',
    description='Provê ponto centralizado de acesso ao MongoDB do Sofie'
)
params.add_argument('-o', '--config', help='URI de acesso ao storage Config', type=str, required=True)
ARGS = params.parse_known_args()[0]


class ConfigStorage(object):
    """
    Classe singleton que acessa o Databse do MongoDB responsável pela configuração do ecossistema MySofie
    """

    __initiated = False
    __storage_point = None

    def __new__(cls, *args, **kwargs):
        """
        Abordagem para tornar a classe singleton

        http://aprenda-python.blogspot.com.br/2012/11/singleton-simples-em-python.html
        """
        if not hasattr(cls, '_instance'):
            cls._instance = super(ConfigStorage, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        """
        Inicialização da instância
        """
        if not ConfigStorage.__initiated:
            ConfigStorage.__initiated = True
            ConfigStorage.__storage_point = MongoClient(ARGS.config)

            # TODO: Contorno para contemporizar os ambientes do Mario e do Thiago versus Produção (Nunes) [SE LIVRAR DISTO O QUANTO ANTES]
            use_credentials = not system() in ('Windows', 'Darwin')

            if use_credentials or True:
                auth: Database = ConfigStorage.__storage_point['admin']
                auth.authenticate('{}'.format('worker'), password='{}'.format('worker@sofie'), source='admin')

            super().__init__()

    @property
    def config(self) -> Database:
        """
        Ponto de acesso único ao storage Config

        :return:
            Instância do client ao storage.
        """
        if not ConfigStorage.__initiated:
            raise MySofieException('ConfigStorage não inicializado')

        return ConfigStorage.__storage_point['config']
