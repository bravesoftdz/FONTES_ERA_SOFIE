[TOC]

# Gestão de Desafios Presenciais



## Dashboard

A primeira tela será um dashboard com um resumo global dos estados das tarefas.

#### API

**Requisição:**

`GET /micro_task/in_person/dashboard`

- `user`: e-Mail do usuário solicitante
- `company`: Nome da empresa para filtro, sendo `prime` para acesso global.



**Resposta:**

`200 - OK`

```json
{
    "state" : {
        "NEW": 1000,
        "WARNING": 0,
        "EXECUTED": 0,
        "AUDITED": 0
    },
    "status" : {
        "WAITING": 1000,
        "APPROVED": 0,
        "DISAPPROVED": 0
    }
}
```



## Mapas

A fim de plotar o mapa utilizando a tecnologia do [Leaflet ](https://leafletjs.com) teremos a chamada abaixo.

#### API

**Host:** https://p2hn9po6p1.execute-api.us-east-1.amazonaws.com/alpha

**Requisição**

`GET /micro_task/in_person/markers`

- `user`: e-Mail do usuário solicitante
- `company`: Nome da empresa para filtro, sendo `prime` para acesso global.

**Resposta:**

`200 - OK`

```json
{
    "markers" : [{
        "task_id": "013d78ef-6034-4e74-8b4c-670ceccce2e4",
        "state": "NEW", 
        "status": "WAITING", 
        "name": "SUPERMERCADO AROMA",
        "address": "Rua Logo Ali, 300, KM 18, Osasco",
        "point": [
            -23.5725951,
            -46.7933088
        ]
     }]
}
```



## Execução de tarefas



### Listagem de execução de uma micro tarefa

Uma tarefa possui uma ou mais tentativas de execução.



#### API

**Host:** https://p2hn9po6p1.execute-api.us-east-1.amazonaws.com/alpha

**Requisição**:

`GET /micro_task/management/{task_id}/execution`

**Resposta:**

`200 - OK`

```json
{
    "data": [
        {
            "task_id": "3be9bdba-49f3-4e7d-aa91-564f11a1e9c8",
            "execution_id": "7b1824f0-bf9d-11e9-a582-ded4e857a9b5",
            "when": {
                "start": "2019-08-15T20:44:34",
                "finish": "2019-08-15T20:45:02"
            },
            "result": 'FINISH',
            "who": "thiago.filadelfo@gmail.com"
        }
    ]
}
```


