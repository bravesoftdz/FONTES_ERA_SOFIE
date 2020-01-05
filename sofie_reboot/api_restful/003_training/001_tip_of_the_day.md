[TOC]

# Dica do dia

A "Dica do Dia" será o prelúdio da área de treinamento da plataforma *Sofie*.

Serão dicas simples, utilizando-se o recurso de *markdown*.



## Listagem de dicas

Retorna a lista de títulos e IDs de dicas.



**Request:**

`GET /training/tips`

**Response:**

`200 - OK`

`Content-Type: application/json`

```json
{
    "data": [
        {
            "content_id": "a54107a5-a499-4570-b7cd-c16efe79c9e3",
            "title": "Use filtro solar"
        } 
    ]
}
```



## Item de dica

Retorna o conteúdo de uma dica específica. Oferece a característica de se indicar se é para trazer a próxima dica em relação ao ID passado.



**Request:**

`GET /training/tips/{content_id}/`



***URL params:***

- `content_id`:  ID do conteúdo desejado. Pode ser utilizado a constante `FIRST` para recuperar a primeira dica.

***Query params:***

- `jump`: Aceita dois valores, a saber: 
  - `next`: Indica que deseja-se a dica posterior 
  - `previous`: ==**NÃO IMPLEMENTADO**== Indica que deseja-se a dica anterior



**Response:**

`200 - OK`

**Content-type:** `application/json`

```json
{
    "content_id": "a54107a5-a499-4570-b7cd-c16efe79c9e3",
    "title": "Use protetor solar",
    "content": "Use protetor solar"
}
```



## Criação de uma nova dica

Define uma nova dica. O chamador recebe o JSON de volta com o `content_id` do novo item.



**Request:**

`POST /training/tips`

`Content-type: application/json`

```json
{
    "title": "Use protetor solar",
    "content": "Use protetor solar",
    "kind": "tip"
}
```



**Response:**

`201 - CREATED`

`Content-type: application/json`

```json
{
    "content_id": "a54107a5-a499-4570-b7cd-c16efe79c9e3",
    "title": "Use protetor solar",
    "content": "Use protetor solar"
}
```



## Exclusão de uma dica

Para excluir uma dica deve-se passar  o ID dela.



**Request:**

`DELETE /training/tips/{content_id}/`

**Response:**

`200 - OK`