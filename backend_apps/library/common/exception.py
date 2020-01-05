# coding: utf-8

"""
Classe base para a criação de exceções personalizadas da plataforma MySofie

O ideal é criar classes descendentes da classe `MySofieException` determinando:

- Um método de inicialização específico
- Uma documentação com explicação detalhada do erroIN_DEBUG_MODE
- Uma mensagem curta, sobrescrevendo o método mágico `__str__`
- Um Status Code HTTP adequado à situação
- Definir propriedades que exporão os parâmetros da exceção para eventual concatenação por parte do frontend

"""

from http import HTTPStatus
from inspect import getmembers


def exception2dict(err: Exception) -> dict:
    """
    Transcreve um `Exception` em dicionário de acordo com as RNs da plataforma

    Basicamente irá um JSON com as seguintes informações:

        - error_code.........: Equivale ao nome da classe de erro, tudo em caixa alta. Caso o erro não seja
                               descendente da classe `MySofieException` irá a string `UNKNOWN`

        - params.............: Dicionário com os properties da classe de erro que serão usados, eventualmente,
                               para concatenar a mensagem de erro no lado cliente

    Caso o servidor REST esteja sendo executado em modo DEBUG serão adicionadas as seguintes informações:

        - status.............: Status HTTP

        - doc................: Documentação da classe de erro, se houver

        - message............: Mensagem original por parte do backend

    :param err:
        Exception
    :return:
        Dicionário
    """
    if isinstance(err, MySofieException):
        status = err.status_http
    else:
        status = HTTPStatus.INTERNAL_SERVER_ERROR.value

    data = {
        'error_code': err.__class__.__name__.upper() if isinstance(err, MySofieException) else 'UNKNOWN',
        'params': {item[0]: getattr(err, item[0], None) for item in getmembers(err.__class__, lambda o: isinstance(o, property))},
        'status': status,
        'doc': err.__doc__.strip() if err.__doc__ else '',
        'message': str(err)
    }

    return data


class MySofieException(Exception):
    """
    Classe base para as exceções da plataforma MySofie
    """

    status_http = HTTPStatus.INTERNAL_SERVER_ERROR.value

    def __init__(self, message: str, status_http: int or None = None):
        """
        Inicialização do objeto

        :param message:
            Mensagem a ser exibida
        :param status_http:
            Sobrescrição do status_http
        """
        self.__message = message
        if status_http:
            self.status_http = status_http

    def __str__(self):
        """
        Conversão do erro para string

        :return:
            String com a mensagem de erro
        """
        return self.__message


class MySofieExceptionBridge(MySofieException):
    """
    Encapsula o erro original para trafegar entre as partes (Microserviço para Rest)
    """

    def __init__(self, soul):
        """

        :param soul:
        """
        self.__soul = soul

    def __str__(self):
        """

        :return:
        """
        return self.__soul['error_code']

    @property
    def soul(self):
        """

        :return:
        """
        return self.__soul


class ResourceNotFound(MySofieException):
    """
    Indica que o recurso solicitado não existe na base de dados ou foi arquivado
    """

    status_http = HTTPStatus.NOT_FOUND.value

    def __init__(self, name: str, resource_class: str):
        """
        Inicializa o objeto

        :param name:
            Nome do recurso
        :param resource_class:
            Nome da classe de recurso em questão
        """
        self.__name = name
        self.__resource_class = resource_class
        super().__init__('O recurso [{}] não foi localizado na classe [{}]'.format(self.__name, self.__resource_class))

    @property
    def name(self):
        return self.__name

    @property
    def resource_class(self):
        return self.__resource_class


class ResourceAlreadyExists(MySofieException):
    """
    Indica que já existe um recurso com o nome solicitado
    """
    status_http = HTTPStatus.BAD_REQUEST.value

    def __init__(self, name: str):
        """
        Inicializa o objeto

        :param name:
            Nome do recurso
        """
        self.__name = name
        super().__init__(f'Algum atributo exclusivo ao recurso [{self.__name}] já existe na base de dados')

    @property
    def name(self):
        """
        Expõe o atributo `name`

        :return:
            `str`
        """
        return self.__name


class ExclusiveOperation(MySofieException):
    """
    Indica que a operação exclusivo para o dono da informação.

    e.g. Somente o Sofier pode mudar a sua foto
    """

    status_http = HTTPStatus.FORBIDDEN.value

    def __init__(self):
        super().__init__('Operação de uso exclusivo ao proprietário da informação')


class UnsupportedFormat(MySofieException):
    """
    Indica que o formato da imagem não é suportado pelo MySofie
    """

    status_http = HTTPStatus.UNSUPPORTED_MEDIA_TYPE.value

    def __init__(self, mime_type: str):
        """
        Inicializa o objeto

        :param mime_type:
            Nome do formato não suportado
        """
        self.__mime_type = mime_type

    def __str__(self):
        return 'Formato de mídia não suportado: {}'.format(self.__mime_type)

    @property
    def mime_type(self):
        """
        Retorna o nome do formato não suportado

        :return:
            Formato
        """
        return self.__mime_type
