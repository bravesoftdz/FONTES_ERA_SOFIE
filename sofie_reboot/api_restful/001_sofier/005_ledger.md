# Livro razão do *sofier*



## Saldos 

Os saldos do *sofier* mudam constantemente de acordo com os eventos na plataforma.



#### API

**Requisição:**

`GET /sofier/{sofier}/balance`

- `sofier`: e-Mail do usuário solicitante

**Resposta:**

`200 - OK`

```json
{
    "VALIDATION": 20,
    "BLOCKED": 0,
    "AVAILABLE": 0,
    "WRONG": 0,
    "has_available_movement": true
}
```



## Extrato de Movimentação



#### API

**Requisição:**

`GET /sofier/{sofier}/balance/statement/{phase}`

- `sofier`: e-Mail do usuário solicitante
- `phase`: Fase em que se encontra a movimentação

**Resposta:**

`200 - OK`

```json
{
    "listing": [{
        "phase": "VALIDATION",
        "task_id": "63148f3c-41b3-40fb-af72-bdf08525e68a",
        "execution_id": "63148f3c-41b3-40fb-af72-bdf08525e68a",
        "reward": 10,
        "sofie_place": {
            "name": "PADARIA DO JOÃO",
        }, 
        "when": "2019-09-02T12:00:00",
        "task": {
            "category": "in_person",
            "type": "inspection",
            "name": "PAT"
        } 
    }]
}
```


