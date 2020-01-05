# coding: utf-8

from datetime import datetime, timedelta
from http import HTTPStatus

from library.common.exception import MySofieException
from library.storage.session import SessionStorage


SCRIPT_LUA_NEAREST = """
--[[
 **BUSCA A PRÓXIMA TAREFA LIVRE DE ACORDO COM A GEO LOCALIZAÇÃO DO SOFIER**
 
 Fluxo:
 ======
  - Verifica se já existe um mostrurário com o _sofier_
    - Se SIM
        - Exclui a chave de mostruário liberando o fluxo normal

  - Recupera a tarefa mais próximo de acordo com os parâmetros
  - Recupera os dados da tarefa
  - Cria chave de mostruário com TTL de 3 minutos
  - Retorna
  
  Condições:
  ==========
   - Tarefa não pode estar sendo apresentada a outro _sofier_
   - Tarefa não pode constar na lista de REJEITADOS pelo _sofier_
   - Tarefa não pode constar na lista de ACEITOS por outros _sofiers_
--]]

local latitude = KEYS[1]
local longitude = KEYS[2]
local radius = KEYS[3]
local sofier = KEYS[4]
local limit_to_reserve = tonumber(KEYS[5])

local TIME2LEAVE = 60 * 5

local count_reserved = #redis.call('KEYS', string.format('SOFIE:MICROTASK:*:RESERVED:%s#', sofier))
if count_reserved >= limit_to_reserve then
    return 'ON_LIMIT'
end

local current_show_case = redis.call('KEYS', string.format('SOFIE:MICROTASK:*:SHOWCASE:%s#', sofier))
if #current_show_case > 0 then
    redis.call('DEL', current_show_case[1])
end

local possibilities = redis.call('GEORADIUS', 'SOFIE:MICROTASK:IN_PERSON#', longitude, latitude, radius, 'km', 'WITHDIST', 'ASC')
local nearest = #possibilities

if nearest == 0 then
    return
end

local task_id
local distance

for i = 1, nearest, 1 do
    nearest = nearest - 1
    -- Dados do item corrente
    task_id, distance = unpack(possibilities[i])
    
    local count_showcase = #redis.call('KEYS', string.format('SOFIE:MICROTASK:%s:SHOWCASE:*#', task_id))
    local count_reserved = #redis.call('KEYS', string.format('SOFIE:MICROTASK:%s:RESERVED:*#', task_id))
    local count_rejected = #redis.call('KEYS', string.format('SOFIE:MICROTASK:%s:REJECTED:%s#', task_id, sofier))
    local count_started  = #redis.call('KEYS', string.format('SOFIE:MICROTASK:%s:IN_EXECUTION:*#', task_id))
    
    if count_showcase + count_reserved + count_rejected + count_started == 0 then
        break
    end
end

-- Preparando a resposta  
local data = redis.call('HGETALL', string.format('SOFIE:MICROTASK:%s:DATA#', task_id))
table.insert(data, 'distance')
table.insert(data, distance)
table.insert(data, 'nearest')
table.insert(data, nearest)
table.insert(data, 'ttl')
table.insert(data, (TIME2LEAVE * 1000) * 0.80)

-- Criando chave de mostruário com TTL de 3'
redis.call('SETEX', string.format('SOFIE:MICROTASK:%s:SHOWCASE:%s#', task_id, sofier), TIME2LEAVE, 'Tarefa RESERVADA!')
  
return data
"""

SCRIPT_LUA_RADAR = """
--[[
  **LISTA A LATITUDE E LONGITUDE DAS LOCALIDADES PRÓXIMAS AO SOFIE**
  
  Fluxo:
  =====
    - Lista todos os rejeitados pelo _sofier_
    - Lista todas as localidades de acordo com os parâmetros
    - Exclui da lista final os rejeitados 
--]]

local latitude = KEYS[1]
local longitude = KEYS[2]
local radius = KEYS[3]
local sofier = KEYS[4]

local do_not_show = {}
local task_id
 
if (sofier ~= '') then
    for i, key_name in ipairs(redis.call('KEYS', string.format('SOFIE:MICROTASK:*:REJECTED:%s#', sofier))) do
        task_id = string.match(key_name, 'SOFIE:MICROTASK:([^:]+)')
        do_not_show[task_id] = true
    end
end

for i, key_name in ipairs(redis.call('KEYS', 'SOFIE:MICROTASK:*:RESERVED:*#')) do
    task_id = string.match(key_name, 'SOFIE:MICROTASK:([^:]+)')
    do_not_show[task_id] = true
end

local possibilities = redis.call('GEORADIUS', 'SOFIE:MICROTASK:IN_PERSON#', longitude, latitude, radius, 'km', 'WITHCOORD', 'ASC')

local final_result = {}
for i, each in ipairs(possibilities) do
    if (do_not_show[each[1]] ~= true) then
        table.insert(final_result, each)
    end
end

return final_result
"""

SCRIPT_LUA_ACCEPT = """
--[[
  **ACEITAÇÃO DE UMA TAREFA POR PARTE DE UM SOFIER**

  Fluxo:
  =====
    - Elimina a chave de exibição da tarefa
    - Cria a chave de "tarefa aceita" pelo _sofier_ com TTL de 2 dias
--]]

local TWO_DAYS = 172800

local sofier = KEYS[1]
local task_id = KEYS[2]
local when = KEYS[3]

redis.call('DEL', string.format('SOFIE:MICROTASK:%s:SHOWCASE:%s#', task_id, sofier))
redis.call('SETEX', string.format('SOFIE:MICROTASK:%s:RESERVED:%s#', task_id, sofier), TWO_DAYS, when)
"""

SCRIPT_LUA_REJECT = """
--[[
 **REJEIÇÃO DE UMA TAREFA POR PARTE DO SOFIER**
 
 Fluxo:
 ======
  - Elimina a chave de exibição da tarefa
  - Cria a chave de "tarefa rejeitada" pelo _sofier_ 
--]]

local sofier = KEYS[1]
local task_id = KEYS[2]
local when = KEYS[3]

local ONE_DAY = 60 * 60 * 24

redis.call('DEL', string.format('SOFIE:MICROTASK:%s:SHOWCASE:%s#', task_id, sofier))
redis.call('SETEX', string.format('SOFIE:MICROTASK:%s:REJECTED:%s#', task_id, sofier), ONE_DAY, when)
"""

SCRIPT_LUA_RESERVEDS = """
--[[
  **LISTAGEM DE TAREFAS RESERVADAS À UM SOFEIR** 
  
  Fluxo:
  ======
   - Lista todas as chaves de tarefas reservadas ao _sofier_ corrente
   - Com cada chave:
       - Recupera os dados
       - Recupera o TTL
       - Adiciona o item à lista de reposta final
--]]

local sofier = KEYS[1]

local final_data = {}
local reserveds_keys = redis.call('KEYS', string.format('SOFIE:MICROTASK:*:RESERVED:%s#', sofier))

for i, item in ipairs(reserveds_keys) do
    local task_id, sofier = string.match(item, 'SOFIE:MICROTASK:([^:]+):RESERVED:([^#]+)#')
    
    local key_data = string.format('SOFIE:MICROTASK:%s:DATA#', task_id)
    local item_data = redis.call('HGETALL', key_data)
    
    local ttl = redis.call('TTL', item)
    table.insert(item_data, 'valid_until')
    table.insert(item_data, ttl)
    
    local when = redis.call('GET', item) 
    table.insert(item_data, 'booked_on')
    table.insert(item_data, when)

    table.insert(item_data, 'sofier')
    table.insert(item_data, sofier)
    
    table.insert(final_data, item_data)        
end

return final_data
"""

SCRIPT_LUA_START = """
--[[
  **SINALIZAÇÃO DE INÍCIO DE EXECUÇÃO DE TAREFA**
  
  Fluxo:
  ======
   - Valida a existência da chave de reserva da `tarefa` em nome do `sofier`
       - NÃO EXISTE
           - Retornar constante `NOT_RESERVED`
       - EXISTE
           - Criar a chave de ínicio de execução com TTL de 3 horas
           - Retornar a constante `SUCCESS` 
--]]

local sofier = KEYS[1]
local task_id = KEYS[2]

local THREE_HOURS = 10800

local is_reserverd = redis.call('EXISTS', string.format('SOFIE:MICROTASK:%s:RESERVED:%s#', task_id, sofier)) > 0

if not is_reserverd then
    return 'NOT_RESERVED'
end

redis.call('SETEX', string.format('SOFIE:MICROTASK:%s:IN_EXECUTION:%s#', task_id, sofier), THREE_HOURS, 'TASK IN PROGRESS')

return 'SUCCESS'
"""

SCRIPT_LUA_FINISH = """
--[[
  **SINALIZAÇÃO DE QUE A TAREFA FOI EXECUTADA**
  
  Fluxo:
  ======
   - Se AÇÃO == FINISHED  
     - Exclui a chave de reserva
     - Exclui a chave de tarefa em execução
     - Exclui a chave de dados da micro tarefa
     - Exclui a localidade do conjunto de tarefas
     
   - Se AÇÃO == CANCEL
     - Exclui a chave de reserva
     - Exclui a chave de tarefa em execução
    
   - Se AÇÃO == POSTPONE
     - Incrementa o TTL de reserva em 24 horas
     - Exclui a chave de tarefa em execução 
     
--]]

local sofier = KEYS[1]
local task_id = KEYS[2]
local action = KEYS[3]

if action == 'FINISH' then
    redis.call('DEL', string.format('SOFIE:MICROTASK:%s:RESERVED:%s#', task_id, sofier))
    redis.call('DEL', string.format('SOFIE:MICROTASK:%s:IN_EXECUTION:%s#', task_id, sofier))
    redis.call('DEL', string.format('SOFIE:MICROTASK:%s:DATA#', task_id))
    redis.call('ZREM', 'SOFIE:MICROTASK:IN_PERSON#', task_id)
    
elseif action == 'CANCEL' then
    redis.call('DEL', string.format('SOFIE:MICROTASK:%s:RESERVED:%s#', task_id, sofier))
    redis.call('DEL', string.format('SOFIE:MICROTASK:%s:IN_EXECUTION:%s#', task_id, sofier))

elseif action == 'POSTPONE' then
    local ONE_DAY = 86400
    local ttl = redis.call('TTL', string.format('SOFIE:MICROTASK:%s:RESERVED:%s#', task_id, sofier))
    redis.call('EXPIRE', string.format('SOFIE:MICROTASK:%s:RESERVED:%s#', task_id, sofier), ONE_DAY + ttl)
    redis.call('DEL', string.format('SOFIE:MICROTASK:%s:IN_EXECUTION:%s#', task_id, sofier))

else
    return 'UNSUCCESS'
    
end

return 'SUCCESS'
"""

SCRIPT_LUA_DASH = """
--[[
    **CONTABILIZAÇÃO DAS TAREFAS RESERVADAS E EM ANDAMENTO**
    
    Fluxo:
    ======
     - 
--]]

local qtt_reserveds = #redis.call('KEYS', 'SOFIE:MICROTASK:*:RESERVED:*#')
local qtt_execution = #redis.call('KEYS', 'SOFIE:MICROTASK:*:IN_EXECUTION:*#')

return {'RESERVED', qtt_reserveds, 'EXECUTION', qtt_execution}
"""

redis_instance = SessionStorage().storage

SHA_SCRIPT_LUA_NEAREST = redis_instance.script_load(SCRIPT_LUA_NEAREST)
SHA_SCRIPT_LUA_RADAR = redis_instance.script_load(SCRIPT_LUA_RADAR)
SHA_SCRIPT_LUA_ACCEPT = redis_instance.script_load(SCRIPT_LUA_ACCEPT)
SHA_SCRIPT_LUA_REJECT = redis_instance.script_load(SCRIPT_LUA_REJECT)
SHA_SCRIPT_LUA_RESERVEDS = redis_instance.script_load(SCRIPT_LUA_RESERVEDS)
SHA_SCRIPT_LUA_START = redis_instance.script_load(SCRIPT_LUA_START)
SHA_SCRIPT_LUA_FINISH = redis_instance.script_load(SCRIPT_LUA_FINISH)
SHA_SCRIPT_LUA_DASH = redis_instance.script_load(SCRIPT_LUA_DASH)

LIMIT_TO_RESERVE = 10


class NotReserved(MySofieException):
    """

    """
    status_http = HTTPStatus.INTERNAL_SERVER_ERROR.value

    def __init__(self, task_id: str, sofier: str):
        """

        :param task_id:
        :param sofier:
        """
        self.__task_id = task_id
        self.__sofier = sofier

        super(NotReserved, self).__init__(f'A tarefa {task_id} não esta reservada para o sofier {sofier}')

    @property
    def task_id(self):
        """
        Expõe o atributo _task_id_
        """
        return self.__task_id

    @property
    def sofier(self):
        """

        :return:
        """
        return self.__sofier


class OnLimit(MySofieException):
    """

    """
    status_http = HTTPStatus.INTERNAL_SERVER_ERROR.value

    def __init__(self, limit: int):
        """

        """
        self.__limit = limit
        super(OnLimit, self).__init__(f'O sofier atingiu o limite de {limit} reservas')

    @property
    def limit(self):
        """

        :return:
        """
        return self.__limit


class MicroTaskReserve(object):
    """
    Aglutina as regras de negócio em relação à reserva de micro tarefas
    """

    def __init__(self, sofier: str):
        """
        Inicializa o objeto

        :param sofier:
            eMail do _sofier_
        """
        super().__init__()
        self.__sofier = sofier

    def __convert_value(self, key, value):
        """
        Conversão do retorno Redis para tipos mais convenientes

        :param key:
            Nome da chave
        :param value:
            Valor da chave
        :return:
            Vavlor convertido
        """
        if isinstance(value, bytes):
            if key == b'csv_row':
                return int(value.decode())
            elif key in (b'lat', b'lng', b'distance', b'reward'):
                return float(value.decode())
            else:
                return value.decode()
        elif isinstance(value, int):
            if key == b'valid_until':
                return datetime.utcnow() + timedelta(seconds=value)
            else:
                return value
        else:
            raise Exception(f'Tipo não suportado: [{value.__class__.__name__}]')

    def next_nearest(self, lat: float, lng: float, radius: float) -> dict:
        """
        Busca o próximo local, obedecendo ao seguinte fluxo:

        :param lat:
            Latitude do Sofier
        :param lng:
            Longitude do Sofier
        :param radius:
            Raio de abrangência da busca
        :return:
            Dados da tarefa localizada bem como a quantidade de outras tarefas potenciais
        """
        data = SessionStorage().storage.evalsha(
            SHA_SCRIPT_LUA_NEAREST,
            5,
            lat,
            lng,
            radius,
            self.__sofier,
            LIMIT_TO_RESERVE if self.__sofier != 'sonia@mysofie.com' else 1000
        )

        if data == b'ON_LIMIT':
            raise OnLimit(LIMIT_TO_RESERVE)

        task, nearest = dict(), 0
        while data:
            key, value, *data = data
            value = self.__convert_value(key, value)

            if key == b'nearest':
                nearest = value
            else:
                task[key.decode()] = value

        return {'task': task, 'nearest': nearest}

    def accept(self, task_id: str) -> bool:
        """
        Processa a **aceitação** de uma tarefa por parte do _sofier_

        :param task_id:
            ID da tarefa em questão
        :return:
            Booolean indicando o sucesso da operação
        """
        data = SessionStorage().storage.evalsha(
            SHA_SCRIPT_LUA_ACCEPT,
            3,
            self.__sofier,
            task_id,
            datetime.utcnow().isoformat()
        )

        return data

    def reject(self, task_id: str):
        """
        Processa a **rejeição** de uma tarefa por parte do _sofier_

        :param task_id:
            ID da tarefa em questão
        :return:
            Boolean indicando o sucesso da operação
        """
        data = SessionStorage().storage.evalsha(
            SHA_SCRIPT_LUA_REJECT,
            3,
            self.__sofier,
            task_id,
            datetime.utcnow().isoformat()
        )

        return data

    def get_reserveds(self) -> dict:
        """
        Retorna a lista de tarefas reservadas pelo _sofier_ ordenado pelo TTL de forma ascendente

        :return:
            Lista com as tarefas reservadas
        """
        data = SessionStorage().storage.evalsha(
            SHA_SCRIPT_LUA_RESERVEDS,
            1,
            self.__sofier
        )

        list_final = list()

        for each in data:
            item = dict()
            while each:
                key, value, *each = each
                value = self.__convert_value(key, value)
                item[key.decode()] = value

            list_final.append(item)

        return {'data': list_final}

    def execution_start(self, task_id: str) -> dict:
        """
        Sinaliza ao sistema que uma determinada tarefa entrou em execução

        :param task_id:
            ID da tarefa em questão
        :return:
            Constante com o resultado da ação
        """
        data = SessionStorage().storage.evalsha(
            SHA_SCRIPT_LUA_START,
            2,
            self.__sofier,
            task_id
        )

        if data == b'NOT_RESERVED':
            raise NotReserved(task_id, self.__sofier)

        return {'message': data.decode()}

    def execution_finish(self, task_id: str, postpone_or_cancel: str):
        """
        Sinaliza ao sistema que uma determinada tarefa foi executada

        :param task_id:
            ID da tarefa em questão
        :param postpone_or_cancel:
            FINISH   - Indica que é para FINALIZAR a tarefa
            POSTPONE - Indica que é para POSTERGAR a tarefa
            CANCEL   - Indica que é para CANCELAR a tarefa
        :return:
            Constante com o resultado da ação
        """
        assert postpone_or_cancel in ('FINISH', 'POSTPONE', 'CANCEL'), f'Ação não reconhecida: [{postpone_or_cancel}]'

        data = SessionStorage().storage.evalsha(
            SHA_SCRIPT_LUA_FINISH,
            3,
            self.__sofier,
            task_id,
            postpone_or_cancel
        )

        return {'message': data.decode()}


def radar(lat: float, lng: float, radius: float, sofier: str or None):
    """

    :return:
    """
    data = SessionStorage().storage.evalsha(
        SHA_SCRIPT_LUA_RADAR,
        4,
        lat,
        lng,
        radius,
        sofier or ''
    )

    return {'data': [{'lat': float(each[1]), 'lng': float(each[0])} for _, each in data]}


def dashboard():
    """

    :return:
    """
    data = SessionStorage().storage.evalsha(SHA_SCRIPT_LUA_DASH, 0)

    buffer = dict()
    while data:
        key, value, *data = data
        buffer[key.decode()] = value

    return buffer


def create_micro_task(data: dict) -> bool:
    """
    Cria uma micro tarefa, colocando-a na arena

    :param data:
        Dados da micro tarefa
    :return:
        Indica que a execução foi efetuada com sucesso
    """
    pipe = SessionStorage().storage.pipeline()
    pipe.hmset(f'SOFIE:MICROTASK:{data["task_id"]}:DATA#', data)
    pipe.geoadd('SOFIE:MICROTASK:IN_PERSON#', data['lng'], data['lat'], data['task_id'])
    pipe.execute()
    return True
