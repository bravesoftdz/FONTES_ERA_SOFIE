# coding: utf-8

"""
Aglutina os artefatos relacionados à gestão de acesso às informações
"""

from http import HTTPStatus
from re import compile
from uuid import uuid1

from library.common.exception import MySofieException
from library.common.miscellaneous import cpf_is_valid
from library.common.paging_info import PagingInfo
from library.storage.session import SessionStorage

EXPERTISES = ('SALE', 'SEARCH', 'SERVICE', 'LEAD')


class InvalidExpertise(MySofieException):
    """
    Indica que o Expertise solicitado é inválido
    """
    status_http = HTTPStatus.BAD_REQUEST.value

    def __init__(self, expertise: str):
        """
        Inicializa o objeto
        """
        self.__expertise = expertise
        super().__init__('A expertise [{}] é inválida'.format(expertise))

    @property
    def expertise(self):
        """
        Expõe o valor da expertise inválida

        :return:
            Expertise inválida
        """
        return self.__expertise


USER_LEVELS = ('APP_MYSOFIE', 'CONSUMER', 'SOFIER', 'COMPANY', 'PLATFORM', 'DEVELOPER', 'PUBLIC')


class UserLevel(object):
    """
    Representa um nível de acesso sendo que no momento reconhecemos qutro níveis:

    - APP_MYSOFIE : Indica que é o aplicativo MySofie
    - CONSUMER    : Indica que é um Consumidor Final
    - SOFIER      : Indica que é um Sofier, seja ninja, seja colaborador
    - COMPANY     : Indica que é um gestor de uma determinada empresa, logo, tem que filtrar os assuntos pela empresa deste
    - PLATFORM    : Indica que é um usuário da plataforma MySofie
    - DEVELOPER   : Indica que é um uso _hard code_ , o que dá acesso ilimitado

    """

    def __init__(self, level: str):
        """
        Inicializa o objeto

        :param level:
            Nome do nível em questão
        """
        assert level in USER_LEVELS, 'O nome do nível {} não é válido'.format(level)
        self.__level = level

    def __str__(self):
        """
        Retorna a representação do nível em uma string

        :return:
            String com o nome do nível
        """
        return self.__level

    def __eq__(self, other):
        """
        Verifica se duas instâncias de `UserLevel` representam o mesmo nível

        :param other:
            O objeto paradgma
        :return:
            Indicação de que representam o mesmo nível, ou não.
        """
        return str(self) == str(other)

    @property
    def as_string(self):
        return self.__level


LEVEL_APP_MYSOFIE = UserLevel(USER_LEVELS[0])
LEVEL_CONSUMER = UserLevel(USER_LEVELS[1])
LEVEL_SOFIER = UserLevel(USER_LEVELS[2])
LEVEL_COMPANY = UserLevel(USER_LEVELS[3])
LEVEL_PLATFORM = UserLevel(USER_LEVELS[4])
LEVEL_DEVELOPER = UserLevel(USER_LEVELS[5])
LEVEL_PUBLIC = UserLevel(USER_LEVELS[6])


class SessionExpired(MySofieException):
    """
    Indica que a sessão não existe ou já expirou
    """
    status_http = HTTPStatus.UNAUTHORIZED.value

    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__('A sessão não existe ou já expirou')


class InvalidCredentials(MySofieException):
    """
    Indica que as credenciais do usuário são inválidas
    """
    status_http = HTTPStatus.UNAUTHORIZED.value

    def __init__(self, user: str):
        """
        Inicializa o objeto
        """
        self.__user = user or '*INDEFINIDO*'
        super().__init__('Credenciais inválidas para [{}]'.format(self.__user))

    @property
    def user(self):
        """

        :return:
        """
        return self.__user


class ProhibitedOperation(MySofieException):
    """
    Indica que a operação ou recurso solicitado é proibido ao usuário solicitante
    """
    status_http = HTTPStatus.FORBIDDEN.value

    def __init__(self, user: str or None = None):
        """
        Inicializa o objeto
        """
        self.__user = user or '*INDEFINIDO*'
        super().__init__('Operação proibida ao usuário corrente: [{}]'.format(self.__user))

    @property
    def user(self):
        """

        :return:
        """
        return self.__user


class SofierBlocked(MySofieException):
    """
    Indica que o usuário está bloqueado
    """
    status_http = HTTPStatus.UNAUTHORIZED.value

    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__('O usuário esta bloqueado')


class MySofieSession(object):
    """
    Representa uma sessão de usuário ou aplicação na plataforma MySofie
    """

    MAX_ATTEMPTS = 3

    LUA_CODE_GET_SESSION = """
    -- REVALIDAÇÃO DE SESSÃO --
    
    local session_key = string.format('MYSOFIE:SESSION:%s#', KEYS[1]) -- Nome da chave da sessão
    local data = redis.call('HMGET', session_key, 'session', 'level', 'user', 'company', 'sofier_alpha') 
    if data[1] then
        redis.call('EXPIRE', session_key, 604800) --Sessão válida por mais 7 dias
        return data
    end
    """

    LUA_CODE_CLOSE_SESSIONS = """
    -- FECHANDO TODAS AS SESSÕES DE UM SOFIER --
    
    local keys = redis.call('KEYS', 'MYSOFIE:SESSION:*#')
    
    for i, k in ipairs(keys) do
        local user_info = redis.call('HMGET', k, 'user')
        if user_info[1] == KEYS[1] then
            redis.call('DEL', k)
        end                
    end
    """

    LUA_CODE_SET_SESSION = """
    -- REGISTRO DE UMA NOVA SESSÃO --
    
    local ttl_value = 3600 -- 1 hora
    
    -- DELETANDO SESSÕES ANTERIORES CASO TRATAR-SE DE UM SOFIER --
    if KEYS[3] == 'SOFIER' then
        ttl_value = 604800 -- 7 dias
    
        local keys = redis.call('KEYS', 'MYSOFIE:SESSION:*#')
        
        for i, k in ipairs(keys) do
            local user_info = redis.call('HMGET', k, 'user')
            if user_info[1] == KEYS[2] then
                redis.call('DEL', k)
            end    
        end
    end

    -- CRIANDO A NOVA SESSÃO --    
    local session_key = string.format('MYSOFIE:SESSION:%s#', KEYS[1]) -- Nome da chave da sessão
    redis.call('HMSET', session_key, 'session', KEYS[1], 'user', KEYS[2], 'level', KEYS[3], 'company', KEYS[4] or '', 'sofier_alpha', KEYS[5] or '')
    redis.call('EXPIRE', session_key, ttl_value) 
    redis.call('DEL', string.format('MYSOFIE:SOFIER:SESSION:%s:FAILURE#', KEYS[1])) -- Exclusão do controle de tentativas
    """

    LUA_CODE_SET_SOFIER_ALPHA = """
    -- DEFINE QUE O SOFIER É ALPHA NA SESSÃO CORRENTE DO MESMO --
    
    local keys = redis.call('KEYS', 'MYSOFIE:SESSION:*#')
    
    for i, k in ipairs(keys) do
        local user_info = redis.call('HMGET', k, 'user')
        if user_info[1] == KEYS[1] then
            redis.call('HSET', k, 'sofier_alpha', KEYS[2])
        end    
    end
    """

    LUA_MAX_ATTEMPTS = """
    -- INCREMENTA AS TENTATIVAS FRUSTRADAS SEGUIDAS --
    
    local key = string.format('MYSOFIE:SOFIER:SESSION:%s:FAILURE#', KEYS[1])
    local qtt = redis.call('INCR', key)
    redis.call('EXPIRE', key, 1800) -- Meia hora
    
    return qtt
    """

    def __init__(self):
        """
        Inicializa o objeto
        """
        self.__session = None
        self.__level = None
        self.__user = None
        self.__company = None
        self.__sofier_alpha = None

    @classmethod
    def set_sofier_alpha_in_session(cls, sofier: str, is_alpha: bool):
        """

        :param sofier:
        :param is_alpha:
        :return:
        """
        SessionStorage().storage.eval(
            MySofieSession.LUA_CODE_SET_SOFIER_ALPHA,
            2,
            sofier,
            1 if is_alpha else 0
        )

    @classmethod
    def close_sofier_sessions(cls, sofier: str):
        """
        Encerra todas as sessões de um determinado sofier

        :param sofier:
            Identificação do _sofier_
        """
        SessionStorage().storage.eval(
            MySofieSession.LUA_CODE_CLOSE_SESSIONS,
            1,
            sofier
        )

    @classmethod
    def create_developer_session(cls):
        """
        Cria uma sessão nível DEVELOPER

        :return:
            Sessão nível DEVELOPER
        """
        obj_session = MySofieSession()
        obj_session._MySofieSession__level = LEVEL_DEVELOPER

        return obj_session

    @classmethod
    def create_public_session(cls):
        """

        :return:
        """
        obj_session = MySofieSession()
        obj_session._MySofieSession__level = LEVEL_PUBLIC

        return obj_session

    @classmethod
    def create_or_return_session(cls, session: str or None = None, user: str or None = None, password: str or None = None, user_agent: str or None = None, bearer: str or None = None):
        """
        Cria ou retorna uma sessão de usuário de acordo com as credenciais passadas

        :param session:
            Código da sessão
        :param user:
            Nome do usuário
        :param password:
            Senha do usuário
        :param user_agent:
            User Agent da aplicação solicitante
        :param bearer:
            Token Bearer (OAuth2)
        :return:
            Objeto que representa a sessão do usuário
        """
        obj_session = MySofieSession()

        #: VALIDANDO POR SESSÃO PRÉ EXISTENTE
        if session:
            data = SessionStorage().storage.eval(MySofieSession.LUA_CODE_GET_SESSION, 1, session)
            if not data:
                raise SessionExpired()
            obj_session._MySofieSession__session = data[0].decode()
            obj_session._MySofieSession__level = UserLevel(data[1].decode())
            obj_session._MySofieSession__user = data[2].decode()
            obj_session._MySofieSession__company = data[3].decode()
            obj_session._MySofieSession__sofier_alpha = data[4].decode()

        #: VALIDANDO POR CREDENCIAIS DE USUÁRIO
        elif user:
            from crud.sofier import SofierCRUD
            from crud.user import UserCRUD
            from library.crud.crud_base import ResourceNotFound

            def create_sofier_session(doc_sofier: dict):
                """
                Cria uma sessão de Sofier. A lógica foi extraída para uma rotina específica a fim de ser invocada em
                vários pontos do escopo base.

                Por tempo indeterminado será tolerado como "salt" o _sofier_id_ e o _name_ (CPF) sendo que com o tempo
                prevalecerá o primeiro.

                :param doc_sofier:
                    Dados do sofier
                """
                if doc_sofier.get('blocked', None):
                    raise SofierBlocked()

                hash_sofier_password = SofierCRUD.hash_sofier_password(sofier_info['sofier_id'], password)
                if hash_sofier_password != sofier_info['password']:
                    hash_sofier_password = SofierCRUD.hash_sofier_password(sofier_info['name'], password)
                    if hash_sofier_password != sofier_info['password']:
                        qtt = SessionStorage().storage.eval(MySofieSession.LUA_MAX_ATTEMPTS, 1, user)
                        if qtt >= MySofieSession.MAX_ATTEMPTS:
                            SofierCRUD(PagingInfo(), DEVELOPER_SESSION).block(sofier_info['sofier_id'], 'Estouro de tentativas')
                        raise InvalidCredentials(user)

                obj_session._MySofieSession__session = str(uuid1())
                obj_session._MySofieSession__level = UserLevel('SOFIER')
                obj_session._MySofieSession__user = sofier_info['sofier_id']
                obj_session._MySofieSession__sofier_alpha = 1 if sofier_info.get('is_alpha', False) else 0

                SessionStorage().storage.eval(
                    MySofieSession.LUA_CODE_SET_SESSION,
                    5,
                    obj_session._MySofieSession__session,
                    obj_session._MySofieSession__user,
                    'SOFIER',
                    '',
                    obj_session._MySofieSession__sofier_alpha
                )

            def create_user_session(doc_user: dict):
                """

                :return:
                """
                hash_user_password = UserCRUD.hash_user_password(password)
                if hash_user_password != doc_user['password']:
                    raise InvalidCredentials(user)

                obj_session._MySofieSession__session = str(uuid1())
                obj_session._MySofieSession__level = UserLevel(doc_user['level'])
                obj_session._MySofieSession__user = user
                obj_session._MySofieSession__company = doc_user['company']

                SessionStorage().storage.eval(
                    MySofieSession.LUA_CODE_SET_SESSION,
                    4,
                    obj_session._MySofieSession__session,
                    user,
                    doc_user['level'],
                    doc_user['company']
                )

            #: TODO: SIMPLIFICAR QUESTÃO DO CPF X EMAIL (CASE SENSITIVE)
            #: VALIDANDO SOFIER PELO CPF
            if cpf_is_valid(user):
                try:
                    sofier_info = SofierCRUD(PagingInfo(fields=['sofier_id', 'name', 'password', 'blocked', 'is_alpha']), DEVELOPER_SESSION).item(user, field='name')
                except ResourceNotFound:
                    raise InvalidCredentials(user)

                create_sofier_session(sofier_info)

            #: VALIDANDO SOFIER PELO EMAIL
            else:
                try:
                    sofier_info = SofierCRUD(PagingInfo(fields=['sofier_id', 'name', 'password', 'blocked', 'is_alpha']), DEVELOPER_SESSION).item(user, field='email')
                except ResourceNotFound:
                    sofier_info = None

                if sofier_info:
                    create_sofier_session(sofier_info)

                #: VALIDANDO USUÁRIO DA PLATAFORMA
                else:
                    try:
                        user_info = UserCRUD(PagingInfo(fields=['name', 'password', 'level', 'company']), DEVELOPER_SESSION).item(user)
                    except ResourceNotFound:
                        raise InvalidCredentials(user)

                    if user_info:
                        create_user_session(user_info)

        #: VALIDANDO PELO BEARER
        elif bearer:
            if bearer == 'EU_SOU_A_LENDA':  #: RVVfU09VX0FfTEVOREE=
                obj_session._MySofieSession__session = 'APP_MYSOFIE'
                obj_session._MySofieSession__level = UserLevel('APP_MYSOFIE')
                obj_session._MySofieSession__user = 'APP_MYSOFIE'
            else:
                raise InvalidCredentials(user_agent)

        #: NADA DEU CERTO :-(
        else:
            raise InvalidCredentials(session or user)

        #: RETORNO
        return obj_session

    @property
    def session(self) -> str:
        """
        Código da sessão corrente no formato string

        :return:
            String
        """
        return self.__session

    @property
    def level(self) -> UserLevel:
        """
        Nível de Usuário

        :return:
            Objeto que representa o nível de usuário
        """
        return self.__level

    @property
    def user(self) -> str:
        """
        Retorno da identificação do usuário

        :return:
            String com a identificação do usuário
        """
        return self.__user

    @property
    def company(self) -> str:
        """
        Expõe o nome da emporesa do usuário, quando aplicável

        :return:
            Nome da empresa, quando aplicável
        """
        return self.__company

    @property
    def sofier_alpha(self) -> bool:
        """
        Indica se o _sofier_ é "alpha", ou seja, apto a ver todos os Cards - de produção e homologação

        :return:
            Indicação de que se trata de um sofier alpha
        """
        return int(self.__sofier_alpha or 0) == 1

    @property
    def stamp(self) -> dict:
        """
        Retorna o carimbo de um usuário

        :return:
            Dicionário com as informações da sessão corrente
        """
        return {
            'user': self.user,
            'session': self.session,
            'company': self.company,
            'level': str(self.level),
            'sofier_alpha': self.sofier_alpha
        }


DEVELOPER_SESSION = MySofieSession.create_developer_session()
PUBLIC_SESSION = MySofieSession.create_public_session()
