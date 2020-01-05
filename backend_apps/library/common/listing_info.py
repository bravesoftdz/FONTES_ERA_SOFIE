# coding: utf-8

"""
Centraliza tipos convenientes para representar objetos que trafergarão no ecossistema MySofie
"""

from math import ceil

from pymongo.cursor import Cursor


class ListingInfo(object):
    """
    Classe que representa um objeto de listagem genérico

    É compatível com a biblioteca PyMongo e bson
    
    - page  : Número da página atual
    - pages : Quantidade total de páginas
    - count : Quantidade de registros sendo retornado
    - total : Quantidade total de registros na collection
    - data  : Lista com os recursos
    
    """

    __slots__ = ('page', 'pages', 'count', 'total', 'data')

    def __init__(self):
        """
        Inicializa o objeto
        """
        self.page = None
        self.pages = None
        self.count = None
        self.total = None
        self.data = None

    @classmethod
    def build_by_cursor(cls, cursor: Cursor):
        """
        Instância e configura uma instância desta classe à partir de um curso do PyMongo
        
        # TODO: Rever definição de `total` X `count`

        :param cursor:
            Cursor do PyMongo
        :return:
            Instância desta classe
        """
        buffer = ListingInfo()
        buffer.count = cursor.count()
        buffer.page = ceil(cursor._Cursor__skip / cursor._Cursor__limit) + 1 if cursor._Cursor__limit else 1
        buffer.pages = ceil(buffer.count / cursor._Cursor__limit) if cursor._Cursor__limit else 1
        buffer.data = [each for each in cursor]
        buffer.total = len(buffer.data)

        return buffer

    def to_dict(self):
        """

        :return:
        """
        return {key: getattr(self, key, None) for key in self.__slots__}
