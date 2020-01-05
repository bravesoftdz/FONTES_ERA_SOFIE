# coding: utf-8

"""
CRUD da classe de recurso USER, aglutinado as regras de negócio referente a este assunto
"""

from base64 import b64decode
from binascii import hexlify
from hashlib import pbkdf2_hmac
from http import HTTPStatus
from uuid import uuid1

from email_templates.send_email_by_template import EMailTemplate
from library.common.exception import MySofieException
from library.common.governance import UserLevel, LEVEL_COMPANY, LEVEL_SOFIER, ProhibitedOperation, MySofieSession, DEVELOPER_SESSION
from library.common.miscellaneous import cpf_is_valid, anonymize_email
from library.common.paging_info import PagingInfo
from library.crud.crud_base import CRUDBase, InvalidDocument, ResourceNotFound
from library.storage.caching import CachingStorage
from scheme.user import SCHEME_USER


class UserCRUD(CRUDBase):
    """
    CRUD da classe de recurso User
    """

    resource_class = 'user'

    scheme = SCHEME_USER

    VALIDATE_TOKEN_RESET = """
    -- VALIDAÇÃO DO TOKEN DE EXPIRAÇÃO DO LINK DE REDEFINIÇÃO DE SENHA --
    -- RETORNA O TEMPO, EM SEGUNDOS, PARA A EXPIRAÇÃO DA CHAVE --

    local keys = redis.call('KEYS', 'MYSOFIE:CACHE:USER:*:FORGOT_PASSWORD#')

    for i, key in ipairs(keys) do
        local token = redis.call('GET', key)
        if KEYS[1] == token then
            local ttl = redis.call('TTL', key)
            return ttl
        end  
    end
    """

    def before_document_is_valid(self, document: dict) -> dict:
        """

        :param document:
        :return:
        """
        from crud.company import CompanyCRUD

        if self.session.level == LEVEL_SOFIER:
            raise ProhibitedOperation(self.session.user)

        #: Validação do CPF
        if 'cpf' in document:
            if not cpf_is_valid(document['cpf']):
                raise InvalidDocument('CPF')

        #: Codificação da senha
        if 'password' in document:
            password = b64decode(document['password']).decode()
            if len(password) < 8:
                raise MySofieException('A senha esta muita curta. Deve conter 8 caracteres no mínimo.', HTTPStatus.BAD_REQUEST.value)
            hash_password = UserCRUD.hash_user_password(password)
            document['password'] = hash_password

        #: Resgatando informações relevantes
        if 'level' not in document or 'company' not in document:
            extra = UserCRUD(PagingInfo(fields=['level', 'company']), DEVELOPER_SESSION).item(document['name'])
            document.update(extra)

        #: Validação da empresa
        if 'company' in document and document['level'] == LEVEL_COMPANY.as_string:
            if not CompanyCRUD(PagingInfo()).exists(document['company']):
                raise ResourceNotFound(document['company'], 'company')

        #: Validação de pemisividade da operação
        if self.session.level == LEVEL_COMPANY:
            if UserLevel(document['level']) != LEVEL_COMPANY or self.session.company != document['company']:
                raise ProhibitedOperation(self.session.user)

        return document

    def archive(self, name: str):
        """

        :param name:
        :return:
        """
        if self.session.level == LEVEL_SOFIER:
            raise ProhibitedOperation(self.session.user)

        extra = UserCRUD(PagingInfo(fields=['level', 'company'])).item(name)

        if self.session.level == LEVEL_COMPANY:
            if extra['level'] != LEVEL_COMPANY.as_string:
                raise ProhibitedOperation(self.session.user)

            if extra['company'] != self.session.company:
                raise ProhibitedOperation(self.session.user)

        return super(UserCRUD, self).archive(name)

    @staticmethod
    def hash_user_password(password: str) -> str:
        """

        :param password:
        :return:
        """
        dk = pbkdf2_hmac('sha512', password.encode(), b'00000000000', 100000)
        return hexlify(dk).decode()

    def validate_token_reset(self, token: str) -> bool:
        """
        Verifica se o token de expiração de senha é válido, ou seja, se a chave correspondente existe no Redis.
        É considerado válido se o TTL for maior ou igual a 15 segundos.

        :param token:
            TOKEN a ser validado
        :return:
            Indicação se o token é válido ou não
        """
        buffer = CachingStorage.execute_script(UserCRUD.VALIDATE_TOKEN_RESET, 1, token)
        return (buffer or 0) >= 15

    def recover_password(self, user: str) -> dict:
        """
        Solicita a recuperação de senha pelo usuário

        :param user:
            ID do usuário
        :return:
        """
        token = str(uuid1())

        user_doc = self.collection.find_one({'name': user}, {'name': 1, 'short_name': 1})
        if not user_doc:
            raise ResourceNotFound(user_doc, 'user')

        link_to_recover = f'https://mysofie.com/prime/reset_password/?token={token}'

        CachingStorage.set_cache(
            f'MYSOFIE:CACHE:USER:{user}:FORGOT_PASSWORD#',
            token,
            60 * 60 * 24
        )

        email = EMailTemplate()
        email.to = user_doc['name']
        email.subject = 'Você solicitou a redefinição da sua senha?'
        email.template = 'reset_password.html'
        email.data = {'link_to_recover': link_to_recover, 'short_name': user_doc['short_name']}
        email.content_id = {'logo': 'logotipo_321X119.png'}
        email.enqueue()

        return {'email': anonymize_email(user_doc['name'])}

    def reset_password(self, user: str, token: str, password: str) -> dict:
        """
        Efetiva a redefinição de senha

        :param user:
            ID do usuário
        :param token:
            Token
        :param password:
        :return:
        """
        redis_key = f'MYSOFIE:CACHE:USER:{user}:FORGOT_PASSWORD#'

        cached_token = CachingStorage.get_cache(redis_key)
        if not cached_token:
            raise ResourceNotFound('token', 'FORGOT_PASSWORD')

        if token != cached_token:
            raise ProhibitedOperation(user)

        self.modify(user, {'password': password, 'blocked': None})

        CachingStorage.clear_cache_by_pattern(redis_key)

        MySofieSession.close_sofier_sessions(user)

        return {'success': True}
