# coding: utf-8

"""
CRUD refererente à classe de recurso TRAINING
"""

from crud.company import CompanyCRUD
from library.common.governance import LEVEL_SOFIER, LEVEL_COMPANY, ProhibitedOperation, DEVELOPER_SESSION
from library.common.paging_info import PagingInfo
from library.crud.crud_base import CRUDBase, ResourceNotFound
from library.storage.relation import RelationStorage
from scheme.training import SCHEME_TRAINING


class TrainingCRUD(CRUDBase):
    """
    CRUD refererente à classe de recurso TRAINING
    """

    resource_class = 'training'

    scheme = SCHEME_TRAINING

    CYPHER = """
    MERGE (t:TRAINING {{name: '{node}'}})
    WITH t
    MATCH (c:COMPANY {{name: '{company}'}})
    MERGE (c)-[:AVAILABLE]->(t)    
    """

    def build_relationship(self, document: dict):
        """
        Registra o relacionamento

        :param document:
            Documento que engatilhou
        """
        RelationStorage().run(TrainingCRUD.CYPHER.format(node=document['name'], company=document['company']))

    def before_document_is_valid(self, document: dict) -> dict:
        """
        Pré validação em especial no tocante à pemissividade

        :param document:
            Documento que engatilhou
        :return:
            Documento eventualmente modificado
        """
        if not CompanyCRUD(PagingInfo(), DEVELOPER_SESSION).exists(document['company']):
            raise ResourceNotFound(document['company'], 'company')

        if self.session.level == LEVEL_SOFIER:
            raise ProhibitedOperation(self.session.user)

        if self.session.level == LEVEL_COMPANY:
            if self.session.company != document['company']:
                raise ProhibitedOperation(self.session.user)

        return document
