# Abertura de Ticket

Para abertura de um ticket de suport é tutilizado a API a seguir.

**Request:**

`POST /sofier/{sofier}/ticket`

- `sofier`: ID do sofier 

**Content-type:** `application\json`

```json
{
    "sofier": "sofier@mysofie.com",
    "content": "Nononononononononon"
}
```



**Response:**

`201 - CREATED`

**Content-type:** `application\json`

```json
{
    "ticket_id": "a54107a5-a499-4570-b7cd-c16efe79c9e3"
}
```



# Listagem de Tickets

A listagem de tickets poderá ser feito pelo *sofier* ou pelo backoffice.



**Request:**

`GET /sofier/{sofier}/ticket`

- `sofier`:  E-Mail do *sofier* que será utilizado como filtro



**Response:**

`200 - OK`

**Content-type:** `application/josn`

```json
{
    "data": [
        {
            "content": "teste",
            "ticket_id": "61f5fbc6-e6eb-11e9-9fec-4a878744fc48",
            "sofier": "mario@arrayof.io",
            "when": "2019-10-04T21:10:24.672487",
            "status": "NEW"
        },
        {
            "content": "Outro teste",
            "ticket_id": "351a2dca-e6eb-11e9-9fec-4a878744fc48",
            "backoffice": {
                "when": "2019-10-10T19:07:28.190491",
                "who": "mario.guedes@mysofie.com"
            },
            "sofier": "mario@arrayof.io",
            "conclusion": {
                "content": "Improcedente",
                "when": "2019-10-10T19:29:06.274659",
                "who": "mario.guedes@mysofie.com"
            },
            "status": "FINISHED",
            "when": "2019-10-04T21:09:09.412225"
        }
    ]
}
```

