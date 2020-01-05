# coding: utf-8

"""
CRUD da classe de recurso EMPRESA, aglutinado as regras de negócio referente a este assunto
"""

from library.common.governance import LEVEL_COMPANY, LEVEL_PLATFORM, LEVEL_DEVELOPER, LEVEL_SOFIER, ProhibitedOperation
from library.common.miscellaneous import cnpj_is_valid
from library.crud.crud_base import CRUDBase, InvalidDocument
from library.crud.crud_mixin_image import CRUDMixinImage
from library.storage.relation import RelationStorage
from scheme.company import SCHEME_COMPANY


class CompanyCRUD(CRUDBase, CRUDMixinImage):
    """
    CRUD da classe de recurso EMPRESA
    """
    resource_class = 'company'

    scheme = SCHEME_COMPANY

    CYPHER_INSERT = """
    MERGE (:COMPANY {{name: '{node}'}})
    """

    def get_keys_to_clear_cache(self, document: dict) -> list:
        """

        :param document:
            Documento que engatilhou a limpeza do cache
        """
        return [
            'MYSOFIE:CACHE:SOFIER:*:CHALLENGE:SUMMARY#'
        ]

    def build_relationship(self, document: dict):
        RelationStorage().run(CompanyCRUD.CYPHER_INSERT.format(node=document['name']))

    def before_document_is_valid(self, document: dict):
        """

        :param document:
        :return:
        """
        if self.session.level not in (LEVEL_PLATFORM, LEVEL_DEVELOPER):
            raise ProhibitedOperation(self.session.user)

        if 'cnpj' in document:
            if not cnpj_is_valid(document['cnpj']):
                raise InvalidDocument('CNPJ inválido')

        return document

    def listing(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        if self.session.level == SCHEME_COMPANY:
            data = super().listing(**kwargs, name=self.session.company)
        elif self.session.level == LEVEL_PLATFORM:
            data = super().listing(**kwargs)
        else:
            # TODO: LISTAR EMPRESAS EM QUE O USUÁRIO ESTEJA NA BLACKLIST E COLOCAR COMO CLÁUSULA DE PESQUISA
            data = super().listing(**kwargs)

        return data

    def item(self, name: str, **kwargs):
        """

        :param name:
        :param kwargs:
        :return:
        """
        if self.session.level == LEVEL_COMPANY:
            if name != self.session.company:
                raise ProhibitedOperation(self.session.user)

        return super().item(name, **kwargs)

    def create(self, name: str, document: dict):
        """

        :param name:
        :param document:
        :return:
        """
        if self.session.level not in (LEVEL_PLATFORM, LEVEL_DEVELOPER):
            raise ProhibitedOperation(self.session.user)

        return super().create(name, document)

    def archive(self, name: str):
        """

        :param name:
        :return:
        """
        if self.session.level != LEVEL_PLATFORM:
            raise ProhibitedOperation(self.session.user)

        return super().archive(name)

    def get_cache_key_name_root(self, resource: str) -> str:
        """

        :param resource:
        :return:
        """
        return 'MYSOFIE:CACHE:COMPANY:{company}:LOGO:'.format(company=resource)

    def gridfs_collection(self) -> str:
        """

        :return:
        """
        return 'company.logo'

    def crud_image_is_allowed(self, operation: str, resource: str) -> bool:
        """

        :param operation:
        :param resource:
        :return:
        """
        if operation != 'R':
            if self.session.level == LEVEL_SOFIER:
                raise ProhibitedOperation(self.session.user)

            if self.session.level == LEVEL_COMPANY and self.session.company != resource:
                raise ProhibitedOperation(self.session.user)

        return True
