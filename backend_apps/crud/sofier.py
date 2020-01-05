# coding: utf-8

"""
CRUD da classe de recurso SOFIER, aglutinado as regras de negócio referente a este assunto
"""

from base64 import b64decode
from binascii import hexlify
from datetime import datetime
from hashlib import pbkdf2_hmac
from http import HTTPStatus
from uuid import uuid1

from crud.policies import PoliciesCRUD, PoliciesAcceptCRUD
from email_templates.send_email_by_template import EMailTemplate
from library.common.exception import MySofieException, ResourceNotFound
from library.common.governance import LEVEL_SOFIER, LEVEL_APP_MYSOFIE, LEVEL_PLATFORM, LEVEL_DEVELOPER, LEVEL_COMPANY, DEVELOPER_SESSION, ProhibitedOperation, MySofieSession
from library.common.miscellaneous import anonymize_email, cpf_is_valid
from library.common.miscellaneous import sanitize_text
from library.common.miscellaneous import to_json
from library.common.rpc_by_cortex import RPCByCortex
from library.crud.crud_base import CRUDBase, InvalidDocument, AllowedLevels, PagingInfo
from library.crud.crud_mixin_image import CRUDMixinImage
from library.storage.caching import apply_caching, CachingStorage, SEVEN_DAYS
from library.storage.relation import RelationStorage
from library.storage.session import SessionStorage
from scheme.sofier import SCHEME_SOFIER


class SofierCRUD(CRUDBase, CRUDMixinImage):
    """
    CRUD da classe de recurso Sofier
    """
    resource_class = 'sofier'

    exclusive_field_name = 'sofier_id'

    scheme = SCHEME_SOFIER

    levels_permissions = AllowedLevels(
        listing=[LEVEL_PLATFORM, LEVEL_COMPANY, LEVEL_DEVELOPER],
        item=[LEVEL_APP_MYSOFIE, LEVEL_SOFIER, LEVEL_PLATFORM, LEVEL_COMPANY, LEVEL_DEVELOPER],
        create=[LEVEL_APP_MYSOFIE, LEVEL_PLATFORM, LEVEL_COMPANY, LEVEL_DEVELOPER],
        archive=[LEVEL_PLATFORM, LEVEL_COMPANY, LEVEL_DEVELOPER],
        modify=[LEVEL_PLATFORM, LEVEL_COMPANY, LEVEL_DEVELOPER, LEVEL_SOFIER]
    )

    CYPHER_INSERT = """
    MERGE (:SOFIER {{name: '{node}'}})
    """

    VALIDATE_TOKEN_RESET = """
    -- VALIDAÇÃO DO TOKEN DE EXPIRAÇÃO DO LINK DE REDEFINIÇÃO DE SENHA --
    -- RETORNA O TEMPO, EM SEGUNDOS, PARA A EXPIRAÇÃO DA CHAVE --
    
    local keys = redis.call('KEYS', 'MYSOFIE:CACHE:SOFIER:*:FORGOT_PASSWORD#')

    for i, key in ipairs(keys) do
        local token = redis.call('GET', key)
        if KEYS[1] == token then
            local ttl = redis.call('TTL', key)
            return ttl
        end  
    end
    """

    @apply_caching('MYSOFIE:CACHE:SOFIER:{1}:DATA:{0.paging_info.fields_hash}#', ttl=SEVEN_DAYS)
    def item(self, name: str, consider_archiveds: bool = False, **kwargs) -> dict:
        """

        :param name:
        :param consider_archiveds:
        :param kwargs:
        :return:
        """
        old_exclusive_field_name = self.exclusive_field_name

        field = kwargs.pop('field', None)

        if field == 'name':
            self.exclusive_field_name = 'name'
        elif field == 'email':
            self.exclusive_field_name = 'email'

        buffer = super().item(name, consider_archiveds, **kwargs)

        if 'sofier_id' in self.paging_info.fields:
            if 'has_new_policies' in self.paging_info.fields:
                buffer['has_new_policies'] = self.has_new_policies(buffer['sofier_id'])

        self.exclusive_field_name = old_exclusive_field_name

        return buffer

    def create(self, name: str or None, document: dict, **kwargs):
        """

        :param name:
        :param document:
        :param kwargs:
        :return:
        """
        buffer = super().create(name, document, **kwargs)

        info_data = {
            'part_type': 'sofier',
            'part_id': name,
            'transaction': None,
            'value': 5,
            'description': 'BONIFICAÇÃO PELO CADASTRO - OBRIGADO!'
        }
        future = RPCByCortex().enqueue(
            exchange='exchange_LEDGER',
            routing_key='SOFIE.LEDGER.ENTRY',
            body=to_json(info_data),
        )
        data = future.result()[1]

        return buffer

    def has_new_policies(self, name: str) -> bool:
        """

        :param name:
        :return:
        """
        current = PoliciesCRUD(PagingInfo(fields=['version']), DEVELOPER_SESSION).item('current')
        accepted = PoliciesAcceptCRUD(PagingInfo(), DEVELOPER_SESSION).collection.count({'accepted': True, 'version': current['version'], '__created__.who.user': name}) > 0

        return not accepted

    def get_keys_to_clear_cache(self, document: dict) -> list:
        """

        :param document:
            Documento que engatilhou a limpeza do cache
        """
        buffer = [
            f'MYSOFIE:CACHE:SOFIER:{document["sofier_id"]}:*#',
            f'MYSOFIE:CACHE:SOFIER:{document["email"]}:*#'
        ]

        if 'name' in document:
            buffer.append(f'MYSOFIE:CACHE:SOFIER:{document["name"]}:*#')

        return buffer

    def get_cache_key_name_root(self, resource: str) -> str:
        """

        :param resource:
        :return:
        """
        return f'MYSOFIE:CACHE:SOFIER:{resource}:PICTURE:'

    def gridfs_collection(self) -> str:
        """
        Retorna uma instância do GridFS já apontando para a collection

        :return:
            Instância do GridFS
        """
        return 'sofier.picture'

    def crud_image_is_allowed(self, operation: str, resource: str) -> bool:
        """
        Método abstrado a ser sobrescrito nas classes descendentes com o objetivo de liberar, ou não, a operação.

        :param operation:
            Operação sendo executada cujos valores são:

            - C : Create
            - R : Retrieve
            - U : Update
            - D : Delete

        :param resource:
            Nome do recurso sendo maniulado

        :return:
            Indica que a operação é permitida `True` ou não `False`
        """
        return True

    def recover_image_default(self, resource: str):
        """

        :param resource:
        :return:
        """
        return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x1e\x00\x00\x00\x1e\x08\x06\x00\x00\x00;0\xae\xa2\x00\x00\x00\tpHYs\x00\x00\x0b\x12\x00\x00\x0b\x12\x01\xd2\xdd~\xfc\x00\x00\x01\x89IDATH\x89\xc5\x97\xfdQ\xc30\x0c\xc5\x9fX\xa0l\xd0n\x807 L\xd0l@G\xe8y\x02&\xf0\xc1\x04\xa4#t\x830\x01\xdd\x80v\x83f\x02q\xe2\x9c\x03\xf2aK`\xca\xbb\xeb?\xa9\xe2\x9fm\xc9O\x0e13\xac\xe2@\xd7\x00\x9c\xbcF\x9e[\xf3\x00\xf2\x9e\x05\xcc\x81*\x00\x0f\x00n\x07\x7f\xed\xe49y>\x16\x07s\xa0\r\x80\xe7DH\x07\xa0"\xcf\x87b`\x0e$\xdb\xfa\xaa\x18O\xe0+\xf2|\xce\x05^if\x17\xb7W\xa3\x05\x80\xad&P\x0b^+\xe3DuI\xb0E7\xff\x05\xeeJ\x82O\x06\xb0\xea\\k\xc1\x8d\x01\xfc\xa8\t\xb2\x9c\xe3\x83"\x7f;\xf2\xbc\xd1\x8cg\xc9\xb1\xb8\xd6K\t(\xac\x96\x89O\xdb\xac{\xaf\x06 ;\xd1h\x1d\xab\x97\xa9\xaa\xa3\x83\xb9/\x8f\xce\xf1\xe78\xd0\xca2\x96\xd62\xeb\xe8^\xb9\x1c\xef\xa5\xb84\x1d+\t\x8e\xed\xaf1:\x97\xe8\x89<\'\xads\x16\x1c\xa1\xad\xd6\x89&\xb4\'\xcf\xb3\xf6\x99\xca\xf1o\xa0\xa25\x07\x9a=\xff\x93`\x0e\xa4\xc9\xa7F\xf7\xb1>F\x1amu\xac\xce\xb7\x02\xd0^\'\xf2<\xaa\xf8\xa9\x15\xab\xfa\xa9A\xcbx{\xc9\x82U\xfd\xd4\xa8*\t\x8e\x95\xbc\xfc\x03\xf0h1\xc3\x15\xbba@!-r\xe0\x8b\xe9\x1b8Z\x9d\xea\x06a\xd4\xe8"q\x89\xaa\xee49\x96U\x8b\xdb\xdcez\xafV\xf2\x85\xe1\xa6Zf\xaeI\xc8\xc1\x97\xd9\xcaq\x90\xc2KU\xbc\xacL\x00\x92\xae6\xd7\xa1~r\x11\x90\t\xc8\xb1\xebu\xb4|3}\x08\xc0;\xe0\x85\x8e\xd7\xd7\xa7\xd8O\x00\x00\x00\x00IEND\xaeB`\x82'

    def build_relationship(self, document: dict):
        """
        Efetua a criação do nó do tipo Sofier, registrando o Sofier pelo CPF

        :param document:
            Documento que engatilhou a operação
        """
        RelationStorage().run(SofierCRUD.CYPHER_INSERT.format(node=document['sofier_id']))

    @staticmethod
    def hash_sofier_password(sofier_id: str, password: str) -> str:
        """
        Determina o HASH da senha do Sofier de acordo com as regras de negócio da Plataforma Sofie

            - Algoritimo:.: `sha512`
            - Salt........: ID do _sofier_ em texto plano
            - Interações..: 100.000

        Referências:
            - https://pt.wikipedia.org/wiki/Alongamento_de_chave

        :param sofier_id:
            CPF do Sofier, que será utilizado como "Salt"
        :param password:
            Senha do usuário propriamente dito
        :return:
            Hash da senha propriamente dita
        """
        dk = pbkdf2_hmac('sha512', password.encode(), sofier_id.encode(), 100000)
        return hexlify(dk).decode()

    def before_document_is_valid(self, document: dict) -> dict:
        """
        O documento que representa o Sofier precisa atender os seguites critérios:

        [X] O par `nome` contêm o CPF do Sofier e por isso precisa ser um CPF válido
        [X] O par `password` passará pelo seguinte processo:
            [X] A senha tem que estar codificado na Base64
            [X] Após a decodificação tem que ter 8 caracteres no mínimo
            [X] Será gerado um hash da senha com o algoritmo `PBKDF2`, utilizando o CPF, em `MD5`, como "salt"

        :param document:
            Documento a ser validado
        :return:
            Indica se o documento é válido ou não
        """
        if self.session.level not in [LEVEL_APP_MYSOFIE, LEVEL_PLATFORM, LEVEL_SOFIER, LEVEL_DEVELOPER]:
            raise ProhibitedOperation(self.session.user)

        if self.session.level == LEVEL_SOFIER:
            if self.session.user != document['sofier_id']:
                raise ProhibitedOperation

        if 'name' in document and document['name']:
            if not cpf_is_valid(document['name']):
                raise InvalidDocument('CPF inválido')

        if 'password' in document:
            password = b64decode(document['password']).decode()
            if len(password) < 8:
                raise MySofieException('A senha esta muita curta. Deve conter 8 caracteres no mínimo.', HTTPStatus.BAD_REQUEST.value)
            hash_password = SofierCRUD.hash_sofier_password(document['sofier_id'], password)
            document['password'] = hash_password

        if 'shop_name' in document:
            document['shop_name'] = ''.join([char for char in sanitize_text(document['shop_name']) if char != '.'])

        return document

    def block(self, sofier: str, reason: str):
        """
        Bloqueia o sofier em questão.

        [X] Criar o par blocked no documento, que indicará que o usuário esta bloqueado
        [X] Deletar imediatamente o controle de tentativas

        :param sofier:
            Indentificação do Sofier
        :param reason:
            Motivo do bloqueio
        """
        self.modify(sofier, {'blocked': {'reason': reason, 'when': datetime.utcnow()}})
        SessionStorage().storage.delete(f'MYSOFIE:SOFIER:SESSION:{sofier}:FAILURE#')

    def recover_password(self, sofier_id: str) -> dict:
        """
        Solicita a recuperação de senha pelo Sofier

        :param sofier_id:
            ID do Sofier
        :return:
        """
        token = str(uuid1())

        sofier_doc = self.collection.find_one({'sofier_id': sofier_id}, {'email': 1, 'short_name': 1, 'shop_name': 1})
        if not sofier_doc:
            raise ResourceNotFound(sofier_id, 'sofier')

        shop_name = sofier_doc.get('shop_name')
        if shop_name:
            link_to_recover = f'https://{shop_name}.mysofie.com/myspace/reset_password/?token={token}'
        else:
            link_to_recover = f'https://mysofie.com/myspace/reset_password/?token={token}'

        CachingStorage.set_cache(
            f'MYSOFIE:CACHE:SOFIER:{sofier_id}:FORGOT_PASSWORD#',
            token,
            60 * 60 * 24
        )

        email = EMailTemplate()
        email.to = sofier_doc['email']
        email.subject = 'Você solicitou a redefinição da sua senha?'
        email.template = 'reset_password.html'
        email.data = {'link_to_recover': link_to_recover, 'short_name': sofier_doc['short_name']}
        email.content_id = {'logo': 'logotipo_321X119.png'}
        email.enqueue()

        return {'email': anonymize_email(sofier_doc['email'])}

    def reset_password(self, sofier_id: str, token: str, password: str) -> dict:
        """
        Efetiva a redefinição de senha

        :param sofier_id:
            ID do Sofier
        :param token:
            Token
        :param password:
        :return:
        """
        redis_key = f'MYSOFIE:CACHE:SOFIER:{sofier_id}:FORGOT_PASSWORD#'

        cached_token = CachingStorage.get_cache(redis_key)
        if not cached_token:
            raise ResourceNotFound('token', 'FORGOT_PASSWORD')

        if token != cached_token:
            raise ProhibitedOperation(sofier_id)

        self.modify(sofier_id, {'password': password, 'blocked': None})

        CachingStorage.clear_cache_by_pattern(redis_key)

        MySofieSession.close_sofier_sessions(sofier_id)

        return {'success': True}

    def validate_token_reset(self, token: str) -> bool:
        """
        Verifica se o token de expiração de senha é válido, ou seja, se a chave correspondente existe no Redis.
        É considerado válido se o TTL for maior ou igual a 15 segundos.

        :param token:
            TOKEN a ser validado
        :return:
            Indicação se o token é válido ou não
        """
        buffer = CachingStorage.execute_script(SofierCRUD.VALIDATE_TOKEN_RESET, 1, token)
        return (buffer or 0) >= 15

    def get_sofier_id(self, cpf_or_email: str) -> str:
        """

        :param cpf_or_email:
        :return:
        """
        if '@' in cpf_or_email:
            field = 'email'
        else:
            field = 'name'

        doc_sofier = self.collection.find_one({field: {'$regex': f'(?i)^{cpf_or_email}$'}}, {'sofier_id': 1})
        if not doc_sofier:
            raise ResourceNotFound(cpf_or_email, 'sofier')

        return doc_sofier['sofier_id']


if __name__ == '__main__':

    import time

    inicio = time.time()
    for i in range(100):
        str_hash = SofierCRUD.hash_sofier_password('19678335832', '12345678')
        print(str_hash)
    fim = time.time()

    print(fim - inicio)
