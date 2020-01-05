# coding: utf-8

"""
Classe mixin responsável por lidar com as imagens de uma determinada classe de recurso.

A implementação é parecida com o fragmento abaixo:

>>> from gridfs import GridFS
>>>
>>> from backend_apps.library.crud.crud_base import CRUDBase
>>> from library.storage.config import ConfigStorage
>>>
>>>
>>> class CRUDFooBar(CRUDBase, CRUDMixinImage):
...
...     def gridfs_collection(self) -> GridFS:
...         return GridFS(ConfigStorage().config, 'foobar.image')
...
...     def get_cache_key_name_root(self, resource: str) -> str:
...         return 'MYSOFIE:CACHE:FOOBAR:{}.IMAGE:'.format(resource)
...
>>>


Esta classe mixin oferece as seguintes características:

- Método abstrato para definir a chave de cacheamento da imagem
- Método abstrato para retornar o nome da collection que será utilizada
- Método abstrato para permitir, ou não, a operação de CREATE, READ e DELETE
- Método abstrato para determinar uma imagem padrão na falta da imagem no banco
- Método concreto para deletar a imagem
- Método concreto para gravar a imagem
- Método concreto para recuperar a imagem

"""

from abc import abstractmethod
from io import BytesIO

from gridfs import GridFS
from PIL import Image

from library.common.exception import UnsupportedFormat, ResourceNotFound
from library.common.governance import ProhibitedOperation
from library.storage.caching import CachingStorage
from library.storage.config import ConfigStorage


class CRUDMixinImage(object):
    """

    """

    @abstractmethod
    def get_cache_key_name_root(self, resource: str) -> str:
        """
        Método abstrado a ser implementado nas classes descendentes cujo retorno será
        o nome da chave de cacheamento da imagem, como por exemplo:

        >>> 'MYSOFIE:CACHE:SOFIER:19678335832:PICTURE:'
        >>> #:             ------ -----------
        >>> #:                |        \.......> NOME DO RECURSO
        >>> #:                \................> CLASSE DO RECURSO
        ...

        As outras partes se referirão á largura e altura da imagem cacheada:

        >>> 'MYSOFIE:CACHE:SOFIER:19678335832:PICTURE:100:100#'
        ...

        :return:
            Nome da chave de cacheamento
        """
        raise NotImplementedError

    @abstractmethod
    def gridfs_collection(self) -> str:
        """
        Retorna uma instância do GridFS já apontando para a collection

        :return:
            Instância do GridFS
        """
        raise NotImplementedError

    @abstractmethod
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
            Nome do recurso sendo manipulado

        :return:
            Indica que a operação é permitida `True` ou não `False`
        """
        return True

    @abstractmethod
    def recover_image_default(self, resource: str) -> bytes:
        """
        Método abstrado a fim de devolver uma imagem padrão em caso de inexistência da imagem solicitada

        :param resource:
            Nome do recurso sendo solicitado
        :return:
            Retorno da imagem em `bytes`
        """
        raise ResourceNotFound(resource, 'undefined')

    def __get_current_user(self) -> str:
        """
        Recupera a identificação do usuário corrente da classe CRUDBase mixada com esta

        :return:
            Identificação do usuário corrente
        """
        user = None
        session = getattr(self, 'session', None)
        if session:
            user = getattr(session, 'user', None)

        return user

    def clear_image(self, resource: str):
        """
        Solicita a exclusão de uma determinada imagem de acordo com o seu ID

        :param resource:
            Nome do recurso (ID) a ser excluído.
        """
        if not self.crud_image_is_allowed('D', resource):
            raise ProhibitedOperation(self.__get_current_user())

        self.gridfs.delete(resource)
        CachingStorage.clear_cache_by_pattern(self.get_cache_key_name_root(resource) + '*#')

    def define_image(self, resource: str, content: bytes):
        """
        Solicita a definição de uma capa de card

        :param resource:
            Nome do recurso
        :param content:
            Contúedo da imagem em Bytes
        """
        if not self.crud_image_is_allowed('C', resource):
            raise ProhibitedOperation(self.__get_current_user())

        image = Image.open(BytesIO(content))

        if image.format not in ('PNG', 'JPG', 'JPEG'):
            raise UnsupportedFormat(image.format)

        gridfs = self.gridfs

        gridfs.delete(resource)
        gridfs.put(content, _id=resource, Name=resource, contentType='image/{}'.format(image.format))
        CachingStorage.clear_cache_by_pattern(self.get_cache_key_name_root(resource) + '*#')

    def recover_image(self, resource: str, w: int or None = None, h: int or None = None) -> tuple:
        """
        Recupera um recurso de imagem, nas dimensões desejadas pela parte solicitante.
        O retorno da imagem é em `PNG`, independentemente do formato armazenado

        São executados os seguintes passos:

        [X] - Verifica se a imagem, com as proporções desejadas, consta no cache
        [X] - Caso não esteja
            [X] - Verifica se a imagem existe, retornado erro em caso negativo
            [X] - Recupera a imagem, redimensionando
            [X] - Armazena a imagem em cache

        :param resource:
            Nome do recurso em questão
        :param w:
            Largura da imagem
        :param h:
            Altura da imagem
        :return:
            Tupla, onde:

             - [0] - Content-Type da imagem
             - [1] - Bytes da imagem
        """

        def _get_from_cache() -> tuple:
            """
            Retorna a imagem do cache, caso exista

            :return:
                Tupla, onde:

                - [0] - Content-Type da imagem
                - [1] - Bytes da imagem
            """
            data = CachingStorage().storage.hmget(
                self.get_cache_key_name_root(resource) + '{width}:{heigth}#'.format(width=w, heigth=h),
                ['content_type', 'content']
            )

            return data[0].decode() if data[0] else data[0], data[1]

        if not self.crud_image_is_allowed('R', resource):
            raise ProhibitedOperation(self.__get_current_user())

        content_type, content = _get_from_cache()

        if not content_type:
            gridfs = self.gridfs

            if gridfs.exists(resource):
                cursor = gridfs.get(resource)
                bytes_image = cursor.read()
            else:
                bytes_image = self.recover_image_default(resource)

            inp = BytesIO(bytes_image)
            out = BytesIO()

            image = Image.open(inp)
            if w and h:
                image.thumbnail((int(w), int(h)), Image.ANTIALIAS)
            image.save(out, 'PNG')

            content_type, content = 'image/png', out.getvalue()

            CachingStorage().storage.hmset(
                self.get_cache_key_name_root(resource) + '{width}:{heigth}#'.format(width=w, heigth=h),
                {'content_type': content_type, 'content': content}
            )

        return content_type, content

    @property
    def gridfs(self) -> GridFS:
        """

        :return:
        """
        return GridFS(ConfigStorage().config, self.gridfs_collection())
