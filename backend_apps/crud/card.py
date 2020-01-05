# coding: utf-8

"""
CRUD da classe de recurso **card**
"""

from uuid import uuid4
from re import compile

from crud.company import CompanyCRUD
from library.common.exception import ResourceNotFound
from library.common.governance import LEVEL_COMPANY, LEVEL_PLATFORM, LEVEL_DEVELOPER, DEVELOPER_SESSION, ProhibitedOperation
from library.common.paging_info import PagingInfo
from library.crud.crud_base import CRUDBase
from library.crud.crud_mixin_image import CRUDMixinImage
from library.storage.caching import apply_caching
from library.storage.relation import RelationStorage
from scheme.card import SCHEME_CARD

TAG_RE = compile(r'</?[^>]*>')


class CardCRUD(CRUDBase, CRUDMixinImage):
    """
    CRUD da classe de recurso **card**
    """

    resource_class = 'card'

    scheme = SCHEME_CARD

    CYPHER = """
    MERGE (d:CARD {{name: '{node}', expertise: '{expertise}'}})
    WITH d
    MATCH (c:COMPANY {{name: '{company}'}})
    MERGE (c)-[:OFFER]->(d)    
    """

    def get_keys_to_clear_cache(self, document: dict) -> list:
        """

        :param document:
            Documento que engatilhou a limpeza do cache
        """
        return [
            'MYSOFIE:CACHE:SOFIER:*:CHALLENGE:*#',
            f'MYSOFIE:CACHE:CARD:{document["name"]}:PREVIEW#',
            'MYSOFIE:CACHE:CARDS:BYCATEGORY#'
        ]

    def build_relationship(self, document: dict):
        """

        :param document:
            Documento que engatilhou o método
        """
        RelationStorage().run(CardCRUD.CYPHER.format(
            node=document['name'],
            expertise=document['expertise'],
            company=document['company']
        ))

    def before_document_is_valid(self, document: dict):
        """

        :param document:
        :return:
        """
        CompanyCRUD(PagingInfo(), DEVELOPER_SESSION).exists(document['company'], raise_exception=True)

        if self.session.level not in [LEVEL_PLATFORM, LEVEL_COMPANY, LEVEL_DEVELOPER]:
            raise ProhibitedOperation(self.session.user)

        if self.session.level == LEVEL_COMPANY:
            if self.session.company != document['company']:
                raise ProhibitedOperation(self.session.user)

        return document

    def create(self, name: str or None, document: dict, **kwargs) -> dict or None:
        """

        :param name:
        :param document:
        :return:
        """
        if not name:
            name = str(uuid4())

        return super().create(name, document, **kwargs)

    @apply_caching('MYSOFIE:CACHE:CARD:{1}:PREVIEW#', 60 * 60 * 24 * 7)
    def info_for_preview(self, name: str) -> dict:
        """
        Gera informações pertinentes à um determinado Card para efeitos de preview nas redes sociais

        e.g. Facebook, LinkedIn, WhatsApp e etc

        :param name:
            Identificação do Card
        :return:
            `dict` com as informações pertinentes ao Card
        """
        buffer = self.item(name)

        return {
            'card': name,
            'title': f"{buffer['title']['title']} - {buffer['title']['sub_title']}",
            'description': TAG_RE.sub('', buffer['description']).strip()
        }

    def gridfs_collection(self) -> str:
        """
        Retorna o GridFS relativo às capas dos cartões

        :return:
            Instância do GridFS
        """
        return 'card.cover'

    def get_cache_key_name_root(self, resource: str) -> str:
        """
        Sobrescrição do método da super classe `CRUDMixinImage` com o intuito de devolver o nome da
        chave de cacheamento.

        :return:
            Raiz do nome da chave
        """
        return f'MYSOFIE:CACHE:CARD:{resource}:COVER:'

    def crud_image_is_allowed(self, operation: str, resource: str) -> bool:
        """
        Para manipular uma imagem de capa de um card as seguintes premissas devem ser observadas:

        [X] - O Card deve existir previamente
        [X] - A imagem de Card é pública
        [X] - Um logotipo publicado não poderá sofrer alterações
        [X] - Somente usuário level `COMPANY` (e da mesma empresa) e `PLATFORM` podem definir a capa de um card


        :param operation:
            Operação que estão sendo executada, sendo uma das letras do CRUD
        :param resource:
            Nome do Card que está sendo manipulado
        :return:
            Indica que a operação é permitida (`True`) ou não (`False`)
        """
        card = self.collection.find_one({'name': resource}, ['company', 'publication.when'])
        if not card:
            raise ResourceNotFound(resource, 'card')

        if operation == 'R':
            return True
        else:
            self.validate_permissions([LEVEL_COMPANY, LEVEL_PLATFORM, LEVEL_DEVELOPER], card['company'])

            try:
                if card['publication']['when']:
                    return False
            except KeyError:
                pass

        return True
