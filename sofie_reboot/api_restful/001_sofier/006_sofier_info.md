[TOC]

# Dados Cadastrais do _Sofier_

A fim de não nos acoplarmos fortemente ao **AWS Cognito** criamos uma tabela e API específicos para armazenar os dados cadastrais do *sofier* cuja chave será o email dele.



## Definição dos dados cadastrais



### API

**Requisição:**

`POST /sofier/{sofier}`

- `sofier`: ID do *sofier* que é o seu email.



**Content-type:**

```json
{
    "sofier": "mario@arrayof.io",
    "short_name": "Mario Guedes",
    "full_name": "José Mario Silva Guedes",
    "document": "123.456.789-00",
    "main_phone": "11988056887",
    "birthday": "2019-09-08",
    "bank_checking_account": {
		"code": "001",
        "name": "Banco do Brasil",
        "agency": "1234",
        "account": "123456",
        "account_digit": "5"
    },
    "when": "2019-09-03T19:36:00" 
}
```



## Recuperação dos dados cadastrais



### API



**Requisição:**

`GET /sofier/{sofier}`

- `sofier`: ID do *sofier* que é o seu email.



**Resposta:**

`200 - OK`

**Content-type:**

```json
{
    "sofier": "mario@arrayof.io",
    "short_name": "Mario Guedes",
    "full_name": "José Mario Silva Guedes",
    "document": "123.456.789-00",
    "main_phone": "11988056887",
    "birthday": "2019-09-08",
    "bank_checking_account": {
		"code": "001",
        "name": "Banco do Brasil",
        "agency": "1234",
        "account": "123456",
        "account_digit": "5",
        "account_type": "corrente"
    },
    "when": "2019-09-03T19:36:00" 
}
```

