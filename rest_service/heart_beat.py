# coding: utf-8

from tornado.web import RequestHandler
from tornado import version

"""
Manipulador padrão para testar a sanidade do servidor REST
"""


class HeartBeat(RequestHandler):
    """
    Manipulador interno para testar a sanidade do servidor REST
    Teste com git
    """

    def get(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        self.set_status(200)
        self.write('<html><body bgcolor=gold><strong>O Servidor REST esta em execução!\n Tornado version {}.</strong></body></html>'.format(version))
        self.finish()
