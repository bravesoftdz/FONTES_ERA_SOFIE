# coding: utf-8

"""
Centralização do ponto de acesso ao Storage Session da plataforma MySofie.

A gestão de sessão é um fator crucial na segurança e velocidade de acesso aos dados da plataforma.
"""

from argparse import ArgumentParser

from redis import StrictRedis

from library.common.exception import MySofieException

params = ArgumentParser(
    prog='SessionStorage',
    usage='Storage de Session da plataforma MySofie',
    description='Provê ponto centralizado de acesso ao REDIS Session do Sofie'
)
params.add_argument('-s', '--session', help='URI de acesso ao storage Session', type=str, required=True)
ARGS = params.parse_known_args()[0]


class SessionStorage(object):
    """
    Classe singleton que acessa o REDIS responsável pelo caching do ecossistema MySofie
    """

    __initiated = False
    __storage_point = None

    def __new__(cls, *args, **kwargs):
        """
        Abordagem para tornar a classe singleton

        http://aprenda-python.blogspot.com.br/2012/11/singleton-simples-em-python.html
        """
        if not hasattr(cls, '_instance'):
            cls._instance = super(SessionStorage, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        """
        Inicialização da instância
        """
        if not SessionStorage.__initiated:
            SessionStorage.__initiated = True

            if ':' in ARGS.session:
                host, port = ARGS.session.split(':')
            else:
                host, port = ARGS.session, 6379

            SessionStorage.__storage_point = StrictRedis(host=host, port=port)

            super().__init__()

    @property
    def storage(self) -> StrictRedis:
        """
        Ponto de acesso único ao storage Config

        :return:
            Instância do client ao storage
        """
        if not SessionStorage.__initiated:
            raise MySofieException('SessionStorage não inicializado')

        return SessionStorage.__storage_point
