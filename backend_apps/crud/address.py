# coding: utf-8

"""

"""

from hashlib import md5

from crud.consumer import ConsumerCRUD
from library.common.governance import ProhibitedOperation
from library.common.miscellaneous import datetime2string
from library.common.miscellaneous import sanitize_text
from library.crud.crud_base import CRUDBase
from library.storage.relation import RelationStorage
from scheme.address import SCHEME_ADDRESS, SCHEME_ADDRESS_ASSOCIATION
from library.common.exception import ResourceAlreadyExists


class AddressAssociationCRUD(CRUDBase):
    """
    CRUD da classe de recurso `address_association
    """

    resource_class = 'address_association'

    scheme = SCHEME_ADDRESS_ASSOCIATION

    levels_permissions = ConsumerCRUD.levels_permissions

    CYPHER_ASSOCIATION = """
    MATCH (a:ADDRESS {name: {address}})
    MATCH (c:CONSUMER {name: {consumer}})
    MERGE (a)-[:PERTENCE{type: {type}}]->(c)
    """

    def build_relationship(self, document: dict):
        """

        :param document:
            Documento que engatilhou o método
        """
        RelationStorage().run(
            AddressAssociationCRUD.CYPHER_ASSOCIATION,
            address=document['name'],
            consumer=document['user'],
            type=document['address_type']
        )


class AddressCRUD(CRUDBase):
    """
    CRUD para interagir com um determinado endereço
    """

    resource_class = 'address'

    scheme = SCHEME_ADDRESS

    levels_permissions = ConsumerCRUD.levels_permissions

    CYPHER_INSERT = """
    MERGE (a:ADDRESS {name: {node}})
    WITH a
    MATCH (s:SOFIER {name: {sofier}})
    MERGE (s)-[:REGISTERED{date:{when}}]->(a)
    """

    def build_relationship(self, document: dict):
        """

        :param document:
            Documento que engatilhou o método
        """
        RelationStorage().run(
            AddressCRUD.CYPHER_INSERT,
            node=document['name'],
            sofier=document['__created__']['who']['user'],
            when=datetime2string(document['__created__']['when'])
        )

    def build_hash(self, document: dict):
        """

        :param document:
        :return:
        """
        hash_base = ','.join([
            sanitize_text(document['address'][pair])
            for pair in ['zip_code', 'country', 'state', 'city', 'district', 'type', 'full_name', 'number', 'complement']
        ])

        hasher = md5()
        hasher.update(hash_base.encode())

        return hasher.hexdigest()

    def create_and_associate_address(self, user: str, user_level: str, address_type: str, content: dict) -> dict:
        """

        :param user:
        :param user_level:
        :param address_type:
        :param content:
        :return:
        """
        name = self.build_hash(content)
        try:
            content = self.create(name, content, force_projection=True)

            AddressAssociationCRUD(self.paging_info, self.session).create(
                content['name'],
                {'address_type': address_type, 'user': user, 'user_level': user_level}
            )
        except ResourceAlreadyExists:
            return {'name': name}
        except Exception:
            raise
        else:
            return {'name': name}

    def archive(self, name: str):
        """

        :param name:
        :return:
        """
        raise ProhibitedOperation(self.session.user)

    def modify(self, name: str, document: dict):
        """

        :param name:
        :param document:
        :return:
        """
        raise ProhibitedOperation(self.session.user)
