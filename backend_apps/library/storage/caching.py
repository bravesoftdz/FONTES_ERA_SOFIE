# coding: utf-8

"""
Centralização do ponto de acesso ao storage Caching da plataforma MySofie

Como sabemos, o processamento mais rápido é aquele que não é feito.
Então faz-se necessário uma estratégia de cacheamento das informações oriundas de processamento.
"""

from argparse import ArgumentParser
from functools import wraps
from json import loads, JSONDecodeError

from redis import StrictRedis

from library.common.debug_mode import IN_DEBUG_MODE
from library.common.exception import MySofieException
from library.common.miscellaneous import object_deserialize
from library.common.miscellaneous import to_json

params = ArgumentParser(
    prog='CachingStorage',
    usage='Storage de Caching da plataforma MySofie',
    description='Provê ponto centralizado de acesso ao REDIS do Sofie'
)
params.add_argument('-c', '--caching', help='URI de acesso ao storage Caching', type=str, required=True)
ARGS = params.parse_known_args()[0]

SEVEN_DAYS = 60 * 60 * 24 * 7


class CachingStorage(object):
    """
    Classe singleton que acessa o REDIS responsável pelo caching do ecossistema MySofie
    """

    __initiated = False
    __storage_point = None

    LUA_CLEAR_CACHE = """
    -- LIMPEZA DE CACHE VIA PADRÃO DE NOME DE CHAVE--

    for i, pattern in ipairs(KEYS) do
        local keys = redis.call('KEYS', pattern)
        if (keys) then
            for i, key in ipairs(keys) do
                redis.call('DEL', key)
            end 
        end
    end
    
    """

    def __new__(cls, *args, **kwargs):
        """
        Abordagem para tornar a classe singleton

        http://aprenda-python.blogspot.com.br/2012/11/singleton-simples-em-python.html
        """
        if not hasattr(cls, '_instance'):
            cls._instance = super(CachingStorage, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        """
        Inicialização da instância
        """
        if not CachingStorage.__initiated:
            CachingStorage.__initiated = True

            if ':' in ARGS.caching:
                host, port = ARGS.caching.split(':')
            else:
                host, port = ARGS.caching, 6379

            CachingStorage.__storage_point = StrictRedis(host=host, port=port)

            super().__init__()

    @classmethod
    def execute_script(cls, script: str, numkeys, *keys_and_args):
        """

        :param script:
        :param numkeys:
        :param keys_and_args:
        :return:
        """
        return CachingStorage.__storage_point.eval(script, numkeys, *keys_and_args)

    @classmethod
    def clear_cache_by_pattern(cls, pattern: str or list):
        """
        Efetua a limpeza do cache à partir de um padrão

        :param pattern:
            Padrão a ser considerado
        """
        if isinstance(pattern, str):
            pattern = [pattern]

        CachingStorage.__storage_point.eval(CachingStorage.LUA_CLEAR_CACHE, len(pattern), *pattern)

    @classmethod
    def get_cache(cls, key_name: str, ttl: int or None = None) -> dict or str or None:
        """

        :param key_name:
        :param ttl:
        :return:
        """
        pipe = CachingStorage().__storage_point.pipeline()
        pipe.get(key_name)
        if ttl:
            if ttl < 0:
                pipe.delete(key_name)
            else:
                pipe.expire(key_name, ttl)

        buffer = pipe.execute()[0]
        if buffer:
            try:
                return loads(buffer, object_hook=object_deserialize)
            except JSONDecodeError:
                return buffer.decode()

    @classmethod
    def set_cache(cls, key_name: str, buffer: dict or str, ttl: int or None):
        """

        :param key_name:
        :param buffer:
        :param ttl:
        :return:
        """
        if isinstance(buffer, dict):
            serialized_buffer = to_json(buffer)
        else:
            serialized_buffer = buffer

        if ttl:
            CachingStorage().__storage_point.setex(key_name, ttl, serialized_buffer)
        else:
            CachingStorage().__storage_point.set(key_name, serialized_buffer)

    @property
    def storage(self) -> StrictRedis:
        """
        Ponto de acesso único ao storage Config

        :return:
            Instância do client ao storage
        """
        if not CachingStorage.__initiated:
            raise MySofieException('CachingStorage não inicializado')

        return CachingStorage.__storage_point


def apply_caching(key_name: str, ttl: int or None = None, callback=None):
    """
    Decorator responsável por cachear o retorno de um método, reutilizando este cache nas chamadas subsequentes.

    Basicamente deve-se decorar o método de uma classe informando o padrão de nomeação para a chave.

    A classe ao qual pertence o método deve expor os atributos que serão utilizados para formatar a string
    do nome da chave.

    No exemplo abaixo espera-se que o objeto tenha o atributo `name` e o TTL será de 60 segundos.

    >>> @apply_caching('MYSOFIE:CACHE:{0.name}:SUB_ASSUNTO#', 60)
    >>> def foo_bar(self, x, y):
    >>>     pass

    :param key_name:
        Nome da chave
    :param ttl:
        Tempo de expiração, quando aplicável
    :param callback:
        Método de callback que será acionado antes do efetivo retorno tendo a seguinte assinatura prevista:

        >>> def function_name(data):
        >>>     # Foo Bar
        >>>     return data

        O retorno deste método é que será considerado para o retorno do decorator em si
    """

    def decorator(method):
        @wraps(method)
        def caching(*args, **kwargs):
            buffer = None
            cacher = CachingStorage()
            resolved_key_name = key_name.format(*args)

            if not IN_DEBUG_MODE:
                buffer = cacher.get_cache(resolved_key_name, ttl)

            if not buffer:
                buffer = method(*args, **kwargs)

                if buffer and not IN_DEBUG_MODE:
                    cacher.set_cache(resolved_key_name, buffer, ttl)

            if callback:
                buffer = callback(buffer)

            return buffer

        return caching

    return decorator
