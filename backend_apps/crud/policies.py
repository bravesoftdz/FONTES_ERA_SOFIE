"""

"""

from hashlib import sha1
from uuid import uuid1

from gridfs import GridFS

from library.common.exception import ResourceNotFound, ResourceAlreadyExists
from library.common.governance import DEVELOPER_SESSION
from library.common.governance import LEVEL_PLATFORM, LEVEL_SOFIER
from library.crud.crud_base import CRUDBase, AllowedLevels
from library.crud.crud_base import PagingInfo
from library.storage.config import ConfigStorage
from scheme.policies import SCHEME_POLICIES, SCHEME_POLICIES_ACCEPT


class PoliciesCRUD(CRUDBase):
    """

    """
    resource_class = 'policies'

    scheme = SCHEME_POLICIES

    exclusive_field_name = 'version'

    levels_permissions = AllowedLevels(
        listing=[LEVEL_PLATFORM],
        item=[LEVEL_PLATFORM, LEVEL_SOFIER],
        create=[LEVEL_PLATFORM],
        archive=[LEVEL_PLATFORM],
        modify=[LEVEL_PLATFORM]
    )

    def get_keys_to_clear_cache(self, document: dict) -> list:
        return [
            'MYSOFIE:CACHE:SOFIER:*:DATA:*#'
        ]

    def item(self, name: str, consider_archiveds: bool = False, **kwargs):
        """

        :param name:
        :param consider_archiveds:
        :param kwargs:
        :return:
        """
        meta = self.collection.find_one({'active': True}, projection={'version': 1}, sort=[('__created__.when', -1)])
        return super().item(meta['version'])

    def get_document(self, version) -> tuple:
        """

        :param version:
        :return:

            Tupla contendo:

            [0] - MIME TYPE do conteúdo
            [1] - Bytes do arquivo
        """
        gridfs = self.grid_fs

        if version == 'current':
            meta = self.collection.find_one({'active': True}, {'version': 1})
            if meta:
                version = meta['version']

        if gridfs.exists(version):
            cursor = gridfs.get(version)
            bytes_image = cursor.read()
        else:
            raise ResourceNotFound(version, 'policies')

        return 'text/markdown', bytes_image

    def set_document(self, version: str, content: bytes):
        """

        :param version:
        :param content:
        :return:
        """
        gridfs = self.grid_fs

        if gridfs.exists(version):
            raise ResourceAlreadyExists(version)

        hasher = sha1()
        hasher.update(content)
        hash_ = hasher.hexdigest()

        meta = self.collection.find_one({'version': version}, {'hash': 1})
        if not meta:
            raise ResourceNotFound(version, 'policies')

        if hash_ != meta['hash']:
            raise Exception('O SHA1 do arquivo enviado não combina com o informado nos metadados')

        gridfs.put(content, _id=version, Name=version, contentType='text/markdown')

    @property
    def grid_fs(self):
        """

        :return:
        """
        return GridFS(ConfigStorage().config, 'policies.documents')


class PoliciesAcceptCRUD(CRUDBase):
    """

    """

    resource_class = 'policies_accept'

    scheme = SCHEME_POLICIES_ACCEPT

    levels_permissions = AllowedLevels(
        listing=[LEVEL_PLATFORM],
        item=[LEVEL_PLATFORM],
        create=[LEVEL_PLATFORM, LEVEL_SOFIER],
        archive=[LEVEL_PLATFORM],
        modify=[LEVEL_PLATFORM]
    )

    def get_keys_to_clear_cache(self, document: dict) -> list:
        from crud.sofier import SofierCRUD

        sofier_info = SofierCRUD(PagingInfo(fields=['name', 'email', 'sofier_id']), DEVELOPER_SESSION).item(document["__created__"]["who"]["user"])

        return [
            f'MYSOFIE:CACHE:SOFIER:{sofier_info["sofier_id"]}:DATA:*#',
            f'MYSOFIE:CACHE:SOFIER:{sofier_info["email"]}:DATA:*#',
            f'MYSOFIE:CACHE:SOFIER:{sofier_info["name"]}:DATA:*#',
        ]

    def create(self, name: str or None, document: dict, **kwargs):
        """

        :param name:
        :param document:
        :param kwargs:
        :return:
        """
        name = name or str(uuid1())
        super(PoliciesAcceptCRUD, self).create(name, document)
