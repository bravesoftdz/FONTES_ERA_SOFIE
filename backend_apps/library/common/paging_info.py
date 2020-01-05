# coding: utf-8

"""
A classe `PagingInfo` concentra as informações de paginação, ordenação, filtro e projeção

No contexto total (HTTP + CRUD) já foram atendidos as seguintes condições:

- [X] Paginação
- [X] Ordenação
- [X] Filtro
- [X] Projeção
"""

from hashlib import md5


class PagingInfo(object):
    """
    A classe `PagingInfo` concentra as informações de paginação, ordenação, filtro e projeção:

    ---------------------------------------------------------------------------------------------------------------------------------
    | Parâmetro       | Propósito                                     | Obrigatório | Default   | Exemplos válidos                  |
    |----------------:|-----------------------------------------------|:-----------:|:---------:|------------------------------------
    | **`per_page`**  | Quantidade de registro por página             | Não         | 5         |                                   |
    | **`page`**      | Número da página solicitada                   | Não         | 1         |                                   |
    | **`sort`**      | Campos e direção de ordenação                 | Não         | name,ASC  | name,ASC name,1 name,DESC name,-1 |
    | **`filter`**    | Parâmetro de filtro                           | Não         |           | name,xpto                         |
    | **`fields`**    | Lista de campos a serem projetados            | **SIM**     |           | name,idade,nascimento             |
    | **`after`**     | Indica se deve retornar a nova representação  | Não         | no        | yes no                            |
    ---------------------------------------------------------------------------------------------------------------------------------

    """
    __slots__ = ('per_page', 'page', 'sort', 'filter', 'fields', 'after', 'fields_hash')

    def __init__(self, **kwargs):
        """
        Inicializa o objeto

        :param kwargs:
            Argumentos opcionais sendo esperado o seguinte:

            - fields : Lista de campos a serem projetados
        """
        self.per_page = None
        self.page = None
        self.sort = None
        self.filter = None
        self.fields = kwargs.get('fields', [])
        self.after = False
        self.fields_hash = self.build_fields_hash()

    def build_fields_hash(self):
        """

        :return:
        """
        fields_to_hash = self.fields.copy()
        fields_to_hash.sort()
        fields_to_hash = ','.join(fields_to_hash)
        if not fields_to_hash:
            fields_to_hash = '*'

        hasher = md5()
        hasher.update(fields_to_hash.encode())

        return hasher.hexdigest()

    @classmethod
    def build_by_handler(cls, handler):
        """
        Construtor que retorna a instância à partir da querystring

        :param handler:
            Manipulador HTTP
        :return:
            Instância desta classe
        """

        def parse_sort(input_: str) -> tuple:
            """
            Normaliza o parâmetro de ordenação para

            :return:
                Tupla aderente à bilioteca PyMomgo onde:

                - [0] Nome do campo
                - [1] Direção de ordenação (1 = ASC, -1 = DESC)
            """
            parts = input_.split(',')
            f = parts[0]
            d = parts[1] if len(parts) > 1 else 'ASC'
            d = 1 if d.upper() in ('ASC', '1') else -1

            return f, d

        sorting = handler.get_arguments('sort', True)
        filtering = handler.get_arguments('filter', True)

        list_fields = list()
        for lot in handler.get_arguments('fields'):
            list_fields.extend(lot.split(','))

        buffer = PagingInfo()
        buffer.per_page = int(handler.get_argument('per_page', 5))
        buffer.page = int(handler.get_argument('page', 1))
        buffer.sort = [parse_sort(item) for item in sorting] if sorting else (('name', 1),)
        buffer.filter = {key: value for key, value in [item.split(',') for item in filtering]} if filtering else None
        buffer.fields = list_fields
        buffer.after = handler.get_argument('after', 'no') == 'yes'
        buffer.fields_hash = buffer.build_fields_hash()

        return buffer
