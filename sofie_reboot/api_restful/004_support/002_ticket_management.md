[TOC]

# Gestão de Tickets



## Dashboard de Tickets

Aqui temos um resumo de todos os tickets da plataforma.



### API

**Requisição:**

`GET /ticket/dashboard`



**Resposta:**

`200 - OK`



```json
{
    "NEW": 5,
    "IN_PROGRESS": 5,
    "FINISHED": 15 
}
```



## Listagem de Tickets

Para a listagem de tickets por um determinado status.



### API

**Requisição:**

`GET /ticket/management?status=NEW`

- `status`: Status para efeitos de filtro. Os valores possíveis são:
  - `NEW`
  - `IN_PROGRESS`
  - `FINISHED`

**Resposta:**

`200 - OK`



```json
{
    "data": [
        {
            "content": "Olá!",
            "ticket_id": "b72a29ba-e6db-11e9-a8f5-4e2f95d2dad8",
            "sofier": "mario@arrayof.io",
            "when": "2019-10-04T19:18:15.673177",
            "status": "NEW"
        }
    ]
}
```



##  Acatando um Ticket

Para que o *back office* possa acatar um ticket é dado o seguinte comando:

**API**

**Requisição:**

`PUT /ticket/management/{sofier}/{ticket_id}`

- `sofier`: ID do Sofier
- `ticket_id`: ID do ticket



```json
{
    "status": "IN_PROGRESS",
    "who": "backoffice@mysofie.com"
}
```



**Resposta:**

`200 - OK`



## Finalizando um Ticket

Para que o *back office* possa, então, finalizar um ticket:

**API**

**Requisição:**

`PUT /ticket/management/{sofier}/{ticket_id}`

- `sofier`: ID do Sofier
- `ticket_id`: ID do ticket



```json
{
    "status": "`FINISHED`",
    "who": "backoffice@mysofie.com",
    "content": "Nononononononono"
}
```



**Resposta:**

`200 - OK`



