[TOC]

# Versão corrente do aplicativo

A fim de alertar o usuário sobre uma nova versão teremos um *endpoint* específico a este fim.

Neste mesmo *endpoint* teremos a informação de que a plataforma está em manutenção ou não



## API



**Request:**



`GET /miscellaneous/app_version`



**Response:**



`200 - OK`

```json
{
    "current_version": "1.0-190909",
    "maintenance": false
}
```



