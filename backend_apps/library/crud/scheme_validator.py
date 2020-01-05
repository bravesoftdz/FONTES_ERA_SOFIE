# coding: utf-8

"""
Aglutina as classes responsáveis pela validação de um esquema JSON para garantir, entre outras, que não haja
um ataque MASS ASSIGNMENT ATTACK
"""

from abc import abstractmethod
from datetime import datetime
from re import compile

from bleach import clean


class SchemeInfoBase(object):
    """
    Classe base para validação de esquema
    """

    def __init__(self, required: bool):
        """
        Inicializa o objeto

        :param required:
            Indica que o campo é obrigatório
        """
        self.__required = required

    def do_exception(self, reason: str = '', json_pair: str or None = None, fragment: str or None = None):
        """
        Gera a exeção `InvalidDocument` ficando um ponto único de manutenção

        :param reason:
            Motivo a ser propagado na exceção
        :param json_pair:
            Par JSON sendo analisado
        :param fragment:
            Valor do fragmento que gerou a exceção
        """
        from library.crud.crud_base import InvalidDocument
        raise InvalidDocument(reason or f'Formato inválido para o campo [{json_pair}]: [{fragment}]')

    @abstractmethod
    def process(self, json_pair: str, fragment: dict or list or str or int or float or bool or datetime or None, consider_required: bool):
        """
        Método abstrato que deve ser reescrito nas classes descendentes

        :param json_pair:
            Para JSON sendo analisado
        :param fragment:
            Fragmento de informação a ser validada
        :param consider_required:
            Indica se deve, ou não, criticar o `required`.
            Isto é útil para não criticar os campos requeridos em uma operação de modificação.
        """
        pass

    @property
    def required(self) -> bool:
        """
        Indica se o campo é obrigatório ou não

        :return:
            Boolean
        """
        return self.__required


class SchemeObject(SchemeInfoBase):
    """
    Responsável por validar um tipo "objeto", equivalente à um dicionário
    """

    def __init__(self, required: bool, dict_pairs: dict or object):
        """
        Inicializa o objeto

        :param required:
            Indica se a informação é obrigatória ou não
        :param dict_pairs:
            Dicionário onde o par indica o nome do par esperado e o valor é necessariamente do tipo `SchemeInfoBase`
        """
        super().__init__(required)

        if isinstance(dict_pairs, dict):
            self.__dict_pairs = dict_pairs
        elif isinstance(dict_pairs, SchemeObject):
            self.__dict_pairs = dict_pairs.dict_pairs

    def process(self, json_pair: str, fragment: dict, consider_required: bool):
        """
        Processa um dicionário aplicando os seguintes critérios

        :param json_pair:
            Para JSON sendo analisado
        :param fragment:
            Dicionário a ser validado
        :param consider_required:
            Indica se deve, ou não, criticar o `required`.
            Isto é útil para não criticar os campos requeridos em uma operação de modificação.
        """
        if not fragment:
            if consider_required and self.required:
                self.do_exception(json_pair, fragment=fragment)

            return

        if not isinstance(fragment, dict):
            self.do_exception(json_pair, fragment=fragment)

        pairs_names_received = set([pair for pair in fragment.keys()])
        pairs_names_expected = set([each for each in self.__dict_pairs.keys()])
        pairs_names_expected.add('__created__')
        pairs_names_expected.add('__version__')

        if '' not in pairs_names_expected:
            difference = pairs_names_received.difference(pairs_names_expected)
            if difference:
                self.do_exception(json_pair, f'Campos não esperados: {",".join(difference)}')

            if consider_required:
                pairs_names_requireds = set([key for key, value in self.__dict_pairs.items() if value.required])
                difference = pairs_names_requireds.difference(pairs_names_received)
                if difference:
                    self.do_exception(json_pair, f'Campos obrigatórios: {",".join(difference)}')

        for key, value in fragment.items():
            validator = self.__dict_pairs.get(key, None)
            if validator:
                validator.process(key, value, consider_required)

    def get_string_fields(self) -> list:
        """
        Obtêm a lista de campos, inclusive aninhados, que são do tipo string

        :return:
            Lista com os campos do tipo string
        """
        buffer = list()

        def __build(root: str or None, scheme):
            for field, _type in scheme.items():
                if isinstance(_type, SchemeString):
                    if root:
                        buffer.append(f'{root}.{field}')
                    else:
                        buffer.append(field)

                elif isinstance(_type, SchemeObject):
                    __build(field, _type.dict_pairs)

        __build(None, self.__dict_pairs)

        return buffer

    @property
    def dict_pairs(self):
        """

        :return:
        """
        return self.__dict_pairs


class SchemeString(SchemeInfoBase):
    """
    Responsável por validar uma string
    """

    def __init__(self, required: bool, regex: str = '.*', allowed_tags: list or None = None):
        """
        Inicialização do objeto

        :param required:
            Indica se o campo é requerido ou não
        :param regex:
            Expressão regular a ser aplicada na string
        :param allowed_tags:
            Lista com as TAGs HTML permitidas
        """
        super().__init__(required)
        self.__regex = compile(regex)
        self.__allowed_tags = allowed_tags

    def process(self, json_pair: str, fragment: str, consider_required: bool):
        """
        Valida uma string

        :param json_pair:
            Para JSON sendo analisado
        :param fragment:
            Fragmento de informação a ser validada
        :param consider_required:
            Indica se deve, ou não, criticar o `required`.
            Isto é útil para não criticar os campos requeridos em uma operação de modificação.
        """
        if not fragment:
            if consider_required and self.required:
                self.do_exception(json_pair, fragment=fragment)

            return

        if not isinstance(fragment, str):
            self.do_exception(json_pair, fragment=fragment)

        if not self.__regex.match(fragment):
            self.do_exception(json_pair, fragment=fragment)

        buffer = clean(
            text=fragment,
            tags=self.__allowed_tags
        )
        if buffer != fragment:
            self.do_exception(json_pair, 'Foi detectado injeção de código no texto')


class SchemeNumber(SchemeInfoBase):
    """
    Responsável por validar um número, seja inteiro, seja real
    """

    def __init__(self, required: bool, real: bool, min_value: int or float or None = None, max_value: int or float or None = None):
        """
        Inicializa o objeto

        :param required:
            Indica se o valor é obrigatório, ou não
        :param real:
            Indica se aceita números reais, ou não
        :param min_value:
            Valor mínimo, se aplicável
        :param max_value:
            Valor máximo, se aplicável
        """
        super().__init__(required)
        self.__real = real
        self.__min_value = min_value
        self.__max_vlaue = max_value

    def process(self, json_pair: str, fragment: int or float or None, consider_required: bool):
        """
        Valida um número

        :param json_pair:
            Para JSON sendo analisado
        :param fragment:
            Fragmento de informação a ser validada
        :param consider_required:
            Indica se deve, ou não, criticar o `required`.
            Isto é útil para não criticar os campos requeridos em uma operação de modificação.
        """
        if fragment is None:
            if consider_required and self.required:
                self.do_exception(json_pair, fragment=fragment)

            return

        if not (isinstance(fragment, int) or isinstance(fragment, float)):
            self.do_exception(json_pair, fragment=fragment)

        if isinstance(fragment, float):
            if not self.__real:
                self.do_exception(json_pair, fragment=fragment)

        if self.__min_value:
            if fragment < self.__min_value:
                self.do_exception(json_pair, 'Valor menor que o esperado')

        if self.__max_vlaue:
            if fragment > self.__max_vlaue:
                self.do_exception(json_pair, 'Valor maior que o esperado')


class SchemeList(SchemeInfoBase):
    """
    Responsável por validar uma lista
    """

    def __init__(self, required: bool, item_validator: SchemeInfoBase):
        """
        Inicializa o objeto

        :param required:
            Indica se o valor é requerido ou não
        :param item_validator:
            Classe validadora dos itens da lista
        """
        super().__init__(required)
        self.__item_validator = item_validator

    def process(self, json_pair: str, fragment: list or None, consider_required: bool):
        """
        Valida uma lista e seus itens

        :param json_pair:
            Para JSON sendo analisado
        :param fragment:
            Fragmento de informação a ser validada
        :param consider_required:
            Indica se deve, ou não, criticar o `required`.
            Isto é útil para não criticar os campos requeridos em uma operação de modificação.
        """
        if not fragment:
            if consider_required and self.required:
                self.do_exception(json_pair, fragment=fragment)

            return

        if not isinstance(fragment, list):
            self.do_exception(json_pair, fragment=fragment)

        for item in fragment:
            self.__item_validator.process(json_pair, item, consider_required)


class SchemeBoolean(SchemeInfoBase):
    """
    Responsável por validar uma boolean
    """

    def process(self, json_pair: str, fragment: bool or None, consider_required: bool):
        """
        Valida um boolean

        :param json_pair:
            Para JSON sendo analisado
        :param fragment:
            Fragmento de informação a ser validada
        :param consider_required:
            Indica se deve, ou não, criticar o `required`.
            Isto é útil para não criticar os campos requeridos em uma operação de modificação.
        """
        if fragment is None:
            if consider_required and self.required:
                self.do_exception(json_pair, fragment=fragment)

            return

        if not isinstance(fragment, bool):
            self.do_exception(json_pair, fragment=fragment)


class SchemeNull(SchemeInfoBase):
    """
    Responsável por validar um valor nulo
    """

    def process(self, json_pair: str, fragment: None, consider_required: bool):
        """
        Valida um null

        :param json_pair:
            Para JSON sendo analisado
        :param fragment:
            Fragmento de informação a ser validada
        :param consider_required:
            Indica se deve, ou não, criticar o `required`.
            Isto é útil para não criticar os campos requeridos em uma operação de modificação.
        """
        if fragment is not None:
            self.do_exception(json_pair, fragment=fragment)


class SchemeDateTime(SchemeInfoBase):
    """
    Responsável por validar um valor datetime
    """

    def process(self, json_pair: str, fragment: datetime or None, consider_required: bool):
        """
        Valida um datetime

        :param json_pair:
            Para JSON sendo analisado
        :param fragment:
            Fragmento de informação a ser validada
        :param consider_required:
            Indica se deve, ou não, criticar o `required`.
            Isto é útil para não criticar os campos requeridos em uma operação de modificação.
        """
        if not fragment:
            if consider_required and self.required:
                self.do_exception(json_pair, fragment=fragment)

            return

        if not isinstance(fragment, datetime):
            self.do_exception(json_pair, fragment=fragment)
