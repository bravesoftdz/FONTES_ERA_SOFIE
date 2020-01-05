# coding: utf-8

"""
Declaração da classe base para um manipulador HTTP da plataforma MySofie

Aglutina rotinas convenientes e aderentes às regras de negócio da plataforma MySofie.

Destacam-se:

 - model_class : Atributo que deve fazer referência a uma classe CRUD, quando aplicável.
 - write_json  : Método que converte uma estrutura Python para JSON
"""

from base64 import b64decode
from http import HTTPStatus
from json import loads

from tornado.web import RequestHandler

from library.common.exception import MySofieException, MySofieExceptionBridge, exception2dict
from library.common.governance import InvalidCredentials, ProhibitedOperation
from library.common.governance import MySofieSession, LEVEL_APP_MYSOFIE, LEVEL_PUBLIC
from library.common.miscellaneous import object_deserialize, to_json
from library.common.paging_info import PagingInfo
from library.crud.crud_base import CRUDBase

HEADER_SESSION = 'X-MYSOFIE-ACCESS-TOKEN'


class SofieHTTPHandler(RequestHandler):
    """
    Classe base para a construção de um manipulador HTTP
    """

    model_class = None

    def __init__(self, *args, **kwargs):
        """
        Inicializa o objeto
        """
        self.__session = None
        self.__model = None
        self.__paging = None
        self.__permissions = None
        self.__content_as_json = None
        super(SofieHTTPHandler, self).__init__(*args, **kwargs)

    def initialize(self, **kwargs):
        """
        Espera-se receber um dicionário
        """
        self.__permissions = kwargs

    def prepare(self):
        """
        Efetua a validação do requisitante, obedecendo aos seguintes critérios:
        """
        #: CORS
        origin = self.request.headers.get('origin')
        if origin and origin.startswith('http://localhost'):
            self.set_header('Access-Control-Allow-Origin', origin)

        #: Definindo o cabeçalho `cache-control`
        if self.set_no_cache_in_response:
            self.set_header('cache-control', 'no-store, no-cache, must-revalidate, max-age=0, s-maxage=0')

        #: Inicializando
        access_token = user = None
        permissions = self.__permissions or dict()
        method = self.request.method
        if method == 'PATCH':
            method = 'PUT'

        #: VALIDANDO SE A CHAMADA É PÚBLICA
        if LEVEL_PUBLIC in permissions.get(method, []) or method == 'OPTIONS':
            self.__session = MySofieSession.create_public_session()

        #: VALIDANDO POR ACCESS TOKEN - COOKIE
        if not self.__session:
            if HEADER_SESSION in self.request.cookies:
                access_token = self.request.cookies[HEADER_SESSION].value
                if access_token:
                    self.__session = MySofieSession.create_or_return_session(session=access_token)

        #: VALIDANDO POR ACCESS TOKEN - HEADER
        if not self.__session:
            access_token = self.request.headers.get(HEADER_SESSION)
            if access_token:
                self.__session = MySofieSession.create_or_return_session(session=access_token)

        #: VALIDANDO POR CREDENCIAIS DO USUÁRIO
        if not self.__session:
            authorization = self.request.headers.get('authorization')
            if authorization:
                if ' ' not in authorization:
                    raise MySofieException('Credenciais inválidas', HTTPStatus.BAD_REQUEST.value)

                scheme, credentials = authorization.split()

                if scheme == 'Basic':
                    user, password = b64decode(credentials).decode().split(':')
                    self.__session = MySofieSession.create_or_return_session(user=user, password=password)
                elif scheme == 'Bearer':
                    bearer = b64decode(credentials).decode()
                    self.__session = MySofieSession.create_or_return_session(bearer=bearer)
                else:
                    raise MySofieException('Esquema de autorização não suportado: {}'.format(scheme), HTTPStatus.BAD_REQUEST.value)

        #: SE TUDO DEU CERTO ...
        if self.__session:
            if self.__session.level != LEVEL_APP_MYSOFIE and self.__session.session:
                self.set_header(HEADER_SESSION, self.__session.session)

            if method != 'OPTIONS':
                if self.__session.level not in permissions.get(method, []):
                    raise ProhibitedOperation(self.__session.user)

        #: OU, SE DEU TUDO ERRADO ...
        else:
            raise InvalidCredentials(access_token or user)

    def write_error(self, status_code, **kwargs):
        """
        Normaliza a propagação de um Exception para o convencionado na plataforma MySofie.

        Sobrescreve o método original da plataforma Tornado
        """
        err = kwargs['exc_info'][1]

        if isinstance(err, MySofieExceptionBridge):
            data = err.soul
        else:
            data = exception2dict(err)

        self.write_json(data, data['status'])

    def __define_status(self, with_content: bool, force_status_code: int or None = None):
        """
        Define o Status HTTP de acordo com o contexto

        :param with_content:
            Indica se há conteúdo de retorno
        :param force_status_code:
            Status HTTP indicado pelo programador
        """
        if not force_status_code:
            verb = self.request.method.upper()
            if verb == 'GET':
                if with_content:
                    if self.check_etag_header():
                        status = HTTPStatus.NOT_MODIFIED.value
                    else:
                        status = HTTPStatus.OK.value
                else:
                    status = HTTPStatus.NOT_FOUND.value
            elif verb == 'POST':
                status = HTTPStatus.CREATED.value
            elif verb in ('PUT', 'PATCH', 'DELETE'):
                if with_content:
                    status = HTTPStatus.OK.value
                else:
                    status = HTTPStatus.NO_CONTENT.value
            else:
                status = HTTPStatus.OK.value
        else:
            status = force_status_code

        self.set_status(status or HTTPStatus.OK.value)

    def write_json(self, content: dict or list or str or None = None, force_status_code: int or None = None):
        """
        Escreve a resposta adequadamente emn JSON

        Caso seja passado o parâmetro `force_status_code` o mesmo será considerando idependentemente de qualquer
        outro contexto.

        :param content:
            Conteúdo a ser enviado ao cliente
        :param force_status_code:
            Indica o código do status HTTP que será considerado.
            Caso não seja passado o código determinará pelo contexto.
        :return:
        """
        if content is not None:
            self.set_header('Content-Type', 'application/json')
            self.write(to_json(content) if not isinstance(content, str) else content)

        self.__define_status(content is not None, force_status_code)

        self.finish()

    def write_binary(self, content: bytes or None, content_type: str, file_name: str or None = None, force_status_code: int or None = None):
        """
        Responde a requisição com um arquivo binário, como imagens, arquivos compactados, planilhas e etc.

        :param content:
            Conteúdo em bytes do arquivo binário
        :param content_type:
            [MIME-TYPE do arquivo](https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Basico_sobre_HTTP/MIME_types/Complete_list_of_MIME_types)
        :param file_name:
            Nome do arquivo para download
        :param force_status_code:
            Status code forçado
        """
        self.__define_status(content is not None, force_status_code)

        if file_name:
            self.set_header('Content-Disposition', f'attachment; filename={file_name}')

        if content:
            self.set_header('Content-Type', content_type)
            self.write(content)

        self.finish()

    def options(self, *args, **kwargs):
        """
        Tem por objetivo validar o CORS.

        O foco principal são os ambientes de desenvolvimento, por isso esta previsto apenas http://localhost,
        independentemente da porta
        """
        origin: str = self.request.headers.get('origin')
        if origin.startswith('http://localhost'):
            self.set_header('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, PATCH')
            self.set_header('Access-Control-Allow-Headers', 'authorization')

            self.__define_status(False, HTTPStatus.OK.value)
        else:
            self.__define_status(False, HTTPStatus.UNAUTHORIZED.value)

    @property
    def session(self) -> MySofieSession:
        """
        Retorna a instância que representa uma sessão de usuário ou aplicação

        :return:
            Instância de `MySofieSession`
        """
        return self.__session

    @property
    def model(self) -> CRUDBase:
        """
        Retorna a instância da classe CRUD associado a este manipulador HTTP

        :return:
            Instância da classe CRUD associado a este manipulador HTTP
        """
        if not self.__model:
            if self.model_class:
                self.__model = self.model_class(self.paging_info, self.session)
            else:
                raise MySofieException(f'Não foi definido uma classe model para este manipulador HTTP: {self.__class__.__name__}')

        return self.__model

    @property
    def paging_info(self) -> PagingInfo:
        """
        Retorna uma instância de PagingInfo

        :return:
            Instância de PagingInfo
        """
        if not self.__paging:
            self.__paging = PagingInfo.build_by_handler(self)

        return self.__paging

    @property
    def content_as_json(self) -> dict or list:
        """
        Retorna o conteúdo deserializado do formato JSON

        :return:
            Objeto Python que representa o JSON trafegado
        """
        if not self.__content_as_json:
            self.__content_as_json = loads(self.request.body, object_hook=object_deserialize)

        return self.__content_as_json

    @property
    def set_no_cache_in_response(self) -> bool:
        """
        Indica se deve-se ou não adicionar o cabeçalho `cache-control` na resposta ao solicitante.

        :return:
            `bool`
        """
        return self.__permissions.get('NO_CACHE', False) if self.__permissions else False
