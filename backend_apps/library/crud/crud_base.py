# coding: utf-8

"""
Classe base para a viabilização dos diversos CRUDs da plataforma

Importante observar:

1. O ObjectID (`_id`) não trafega e é desconsiderado para efeitos de busca
2. O documento tem uma versão, que é um número inteiro no par `__version__`
3. A chave única, em geral, se dará pelo par `name`
4. As informações sobre a criação do recurso estará no par `__created__`
5. As informações sobre o arquivamento do recurso estará no par `__archived__`
"""

from abc import abstractmethod
from collections import namedtuple
from datetime import datetime
from http import HTTPStatus

from pymongo.collection import ReturnDocument, Collection
from pymongo.errors import DuplicateKeyError

from library.common.exception import ResourceNotFound, MySofieException, ResourceAlreadyExists
from library.common.governance import MySofieSession, LEVEL_PLATFORM, LEVEL_DEVELOPER, LEVEL_COMPANY
from library.common.governance import ProhibitedOperation
from library.common.listing_info import ListingInfo
from library.common.paging_info import PagingInfo
from library.crud.scheme_validator import SchemeInfoBase
from library.storage.caching import CachingStorage
from library.storage.config import ConfigStorage
from library.storage.relation import RelationStorage

RESTRICTED_FIELDS = ['_id', '__version__', '__archived__', '__created__', 'password']


class InvalidDocument(MySofieException):
    """
    Indica que o documento não atende às regras da entidade correspondente
    """

    status_http = HTTPStatus.BAD_REQUEST.value


AllowedLevels = namedtuple('AllowedLevels', ('listing', 'item', 'create', 'archive', 'modify'))


class CRUDBase(object):
    """
    Classe base de CRUD lidando com os diversos storages da plataforma
    """

    resource_class = None

    scheme = None

    exclusive_field_name = 'name'

    levels_permissions = AllowedLevels(
        listing=[LEVEL_PLATFORM, LEVEL_COMPANY, LEVEL_DEVELOPER],
        item=[LEVEL_PLATFORM, LEVEL_COMPANY, LEVEL_DEVELOPER],
        create=[LEVEL_PLATFORM, LEVEL_COMPANY, LEVEL_DEVELOPER],
        archive=[LEVEL_PLATFORM, LEVEL_COMPANY, LEVEL_DEVELOPER],
        modify=[LEVEL_PLATFORM, LEVEL_COMPANY, LEVEL_DEVELOPER]
    )

    CYPHER_DELETE = "MATCH (node:{label} {{name: '{node}'}}) DETACH DELETE node"

    def __init__(self, pagin_info: PagingInfo, session: MySofieSession or None = None):
        """
        Inicializa a instância
        """
        assert self.resource_class, 'Não foi definido o nome da collection correspondente à Classe de Recurso'
        self.__collection = ConfigStorage().config[self.resource_class]
        self.__paging_info = pagin_info
        self.__session = session

    def validate_permissions(self, permissions: list, company: str or None):
        """
        Valida as permissões da sessão corrente em relação ao atributo de classe `levels_permissions`
        gerando excessão caso a não haja a permissão.

        :param permissions:
            Lista com os níveis permitidos a executarem a ação
        :param company:
            Nome da empresa a que se refere a ação, quando aplicável
        """
        if self.session.level == LEVEL_DEVELOPER:
            return

        if self.session.level not in permissions:
            raise ProhibitedOperation(self.__session.user)

        if self.session.level == LEVEL_COMPANY and company:
            if company != self.session.company:
                raise ProhibitedOperation(self.__session.user)

    @abstractmethod
    def build_relationship(self, document: dict):
        """
        Método a ser sobrescrito nas classes descendentes com o propósito de refazer os relacionamentos no Neo4J

        :param document:
            Documento que engatilhou o método
        """
        pass

    @abstractmethod
    def get_keys_to_clear_cache(self, document: dict) -> list:
        """
        Método a ser sobrescrito nas classes descendentes com o propósito de devolver a lista de chaves para limpeza de
        cache

        :param document:
            Documento que engatilhou a limpeza do cache
        """
        pass

    @abstractmethod
    def before_document_is_valid(self, document: dict) -> dict:
        """

        :param document:
        :return:
        """
        return document

    def validate_document(self, document: dict, is_create: bool) -> bool:
        """
        A classe CRUD deve declarar um atributo referenciando umaa estrutura que representa o esquema
        da classe de recurso em questão.

        O documento poderá ser previamente validando sobrescrevendo-se o método `before_document_is_valid`

        :param document:
            Documento a ser validado
        :param is_create:
            Indica se é um processo de inserção `True` ou modificação `False`
        :return:
            Indica se o documento é válido `True` ou não `False`
        """
        document = self.before_document_is_valid(document)

        if isinstance(self.scheme, SchemeInfoBase):
            self.scheme.process('root', document, is_create)

        return True

    def clear_cache(self, document: dict):
        """
        Efetua a limpeza do cache

        [X] Invoca o o método `on_clear_cache`
        [ ] Efetua o PUB/SUB

        TODO: Efetuar o PUB/SUB

        :param document:
            Documento que engatilhou a limpeza do cache
        """
        keys = self.get_keys_to_clear_cache(document)
        if keys:
            CachingStorage().clear_cache_by_pattern(keys)

    def item(self, name: str, consider_archiveds: bool = False, **kwargs) -> dict:
        """
        Recupera um item específico pelo nome, entre outras condições

        :param name:
            Nome do recurso, que fica no para `name`
        :param consider_archiveds:
            Indica se deve-se considerar os itens arquivados na busca
        :param kwargs:
            Filtros adicionais
        :return:
            Dicionário representando o documento
        """
        self.validate_permissions(self.levels_permissions.item, getattr(self.session, 'company', None))

        predicate = {self.exclusive_field_name: name}

        if not consider_archiveds:
            predicate['__archived__'] = {'$exists': False}

        if kwargs:
            predicate.update(kwargs)
        if self.session.level == LEVEL_COMPANY:
            predicate['company'] = self.session.company

        projection = {'_id': 0}
        if self.__paging_info.fields:
            projection.update({key: 1 for key in self.__paging_info.fields if self.__session.level == LEVEL_DEVELOPER or name not in RESTRICTED_FIELDS})
        else:
            projection.update({key: 0 for key in RESTRICTED_FIELDS} if not self.__session.level == LEVEL_DEVELOPER else {})

        buffer = self.__collection.find_one(predicate, projection=projection)
        if buffer is None:
            raise ResourceNotFound(name, self.resource_class)

        return buffer

    def listing(self, consider_archiveds: bool = False, **kwargs) -> dict:
        """
        Retorna uma listagem da classe de recurso em questão conforme parâmetros em `self.__paging_info`

        :param consider_archiveds:
            Indica se deve-se considerar os itens arquivados na busca
        :param kwargs:
            Filtros adicionais
        :return:
            Dicionário de listagem padrão
        """
        self.validate_permissions(self.levels_permissions.listing, None)

        if not self.__paging_info.fields:
            if self.session.level != LEVEL_DEVELOPER:
                raise MySofieException('Não foi definido uma lista de campos para projeção', HTTPStatus.BAD_REQUEST.value)

        predicate = dict()
        if kwargs:
            predicate.update(kwargs)
        if self.__paging_info.filter:
            predicate.update(self.__paging_info.filter)

        if predicate and self.scheme is not None:
            list_string_fields = self.scheme.get_string_fields()
            for field, value in predicate.items():
                if field in list_string_fields and isinstance(value, str):
                    predicate[field] = {'$regex': value}

        if self.session.level == LEVEL_COMPANY:
            predicate['company'] = self.session.company

        if not consider_archiveds:
            predicate['__archived__'] = {'$exists': False}

        projection = {'_id': 0}
        if self.__paging_info.fields:
            projection.update({name: 1 for name in self.__paging_info.fields if name not in RESTRICTED_FIELDS})

        cursor = self.__collection.find(filter=predicate, projection=projection)

        if self.__paging_info.sort:
            cursor.sort(self.__paging_info.sort)

        if self.__paging_info.per_page:
            cursor.skip(self.__paging_info.per_page * (self.__paging_info.page - 1)).limit(self.__paging_info.per_page)

        return ListingInfo.build_by_cursor(cursor).to_dict()

    def create(self, name: str or None, document: dict, **kwargs) -> dict or None:
        """
        Solicita a criação de um novo recurso. Observar que:

        [X] - Validação do nível de permissão
        [X] - É adicionado o par __version__ com o valor 1
        [X] - Os pares reservados serão ignorados, como `_id` e `__version__`
        [X] - É registrado o momento e autor da criação no par `__creation__`
        [X] - Não permite a criação de item com o mesmo nome no par `name`
        [X] - O retorno da representação esta condicionado ao `self.__paging_info.after`
        [X] - Acionar limpeza do cache
        [X] - Registrar o autor da criação

        :param name:
            Nome do recurso
        :param document:
            Documento a ser inserido
        :param kwargs:
            - force_projection: Força a projeção dos campos
        :return:
            Documento inserido
        """
        try:
            force_projection = kwargs.get('force_projection', False)

            self.validate_permissions(self.levels_permissions.create, document.get('company'))

            if self.exists(name):
                raise ResourceAlreadyExists(name)

            document = {
                key: value for key, value in document.items()
                if self.session.level == LEVEL_DEVELOPER or key not in RESTRICTED_FIELDS or key == 'password'
            }

            document[self.exclusive_field_name] = name

            self.validate_document(document, True)

            if '__version__' not in document:
                document['__version__'] = 1

            if '__created__' not in document:
                document['__created__'] = {'when': datetime.utcnow(), 'who': self.session.stamp}

            self.__collection.insert_one(document)

            self.build_relationship(document)

            self.clear_cache(document)

            if self.__paging_info.after or force_projection:
                return {key: value for key, value in document.items() if key not in RESTRICTED_FIELDS}

        except DuplicateKeyError:
            raise ResourceAlreadyExists(name)
        except Exception:
            raise

    def modify(self, name: str, document: dict) -> dict or None:
        """
        Solicita a modificação de um recurso. Observar que:

        [X] - Sempre será incrementado o número da versão (__version__)
        [X] - Os pares reservados serão ignorados, como _id e __version__
        [ ] - O histório da alteração será registrado em algum lugar
        [X] - O retorno da representação esta condicionado ao `self.__paging_info.after`
        [X] - Acionar limpeza do cache
        [X] - Criação do nó no Neo4J

        :param name:
            Nome do recurso
        :param document:
            Documento, inteiro ou parcial
        :return:
            Nova versão do documento
        """
        old_document = self.__collection.find_one({self.exclusive_field_name: name}, {'_id': 1, 'company': 1})
        if not old_document:
            raise ResourceNotFound(name, self.resource_class)

        self.validate_permissions(self.levels_permissions.modify, old_document.get('company'))

        document = {
            key: value for key, value in document.items()
            if self.session.level == LEVEL_DEVELOPER or key not in RESTRICTED_FIELDS or key == 'password'
        }
        document[self.exclusive_field_name] = name

        self.validate_document(document, False)

        new_document = self.__collection.find_one_and_update(
            filter={'_id': old_document['_id']},
            update={'$set': document, '$inc': {'__version__': 1}},
            return_document=ReturnDocument.AFTER
        )

        self.build_relationship(new_document)

        self.clear_cache(new_document)

        return self.item(name) if self.paging_info.after else None

    def archive(self, name: str) -> dict or None:
        """
        Solicita o arquivamento de um recurso. O arquivamento é caracterizado pela presença do par
        `__archived__` com informações a respeito do arquivamento

        [X] - É incrementado o número da versão
        [X] - É criado o par `__archive__`
        [ ] - O histório da alteração será registrado em algum lugar
        [X] - O retorno da representação esta condicionado ao `self.__paging_info.after`
        [X] - Acionar limpeza do cache
        [X] - Deleção do nó no Neo4J

        TODO: Registrar o autor do arquivamento

        :param name:
            Nome do recurso arquivado
        :return:
            Representação do recurso arquivado
        """
        old_document = self.__collection.find_one({self.exclusive_field_name: name})
        if not old_document:
            raise ResourceNotFound(name, self.resource_class)

        self.validate_permissions(self.levels_permissions.archive, old_document.get('company'))

        new_document = self.__collection.find_one_and_update(
            filter={self.exclusive_field_name: name, '__archived__': {'$exists': False}},
            update={'$set': {'__archived__': {'when': datetime.utcnow(), 'who': None}}, '$inc': {'__version__': 1}},
            projection={key: 0 for key in RESTRICTED_FIELDS},
            return_document=ReturnDocument.AFTER
        )

        RelationStorage().run(CRUDBase.CYPHER_DELETE.format(label=self.resource_class.upper(), node=name))

        self.clear_cache(new_document)

        return new_document if self.__paging_info.after else None

    def exists(self, name: str, raise_exception: bool = False) -> bool:
        """
        Verifica meramente a existência de um recurso pelo seu nome

        :param name:
            Nome do recuro
        :param raise_exception:
            Gera exception caso o documento não exista
        :return:
            Indicação da existência do recurso
        """
        buffer = self.__collection.find_one({self.exclusive_field_name: name}, projection={self.exclusive_field_name: 1, '_id': 0})

        if buffer is None:
            if raise_exception:
                raise ResourceNotFound(name, self.resource_class)

        return buffer is not None

    @property
    def session(self) -> MySofieSession:
        """
        Expõe a sessão de usuário que esta acionando o CRUD em questão

        :return:
            `MySofieSession`
        """
        return self.__session

    @property
    def paging_info(self) -> PagingInfo:
        """

        :return:
        """
        return self.__paging_info

    @property
    def collection(self) -> Collection:
        """
        Expõe a collection referente ao CRUD em questão

        :return:
            `Collection`
        """
        return self.__collection
