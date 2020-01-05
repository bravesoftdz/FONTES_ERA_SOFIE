[TOC]

# Backlog de Micro tarefas



## Listagem das micro tarefas presenciais

API para a listagem das micro tarefas presenciais.

#### API

**Host:** https://p2hn9po6p1.execute-api.us-east-1.amazonaws.com/alpha

**Requisição**:

`GET /micro_task/management/`

- `user`: e-Mail do usuário
- `company`: Nome da empresa, sendo `prime` para um acesso global
- `type`: Tipo de micro-tarefa sendo o valor suportado: `in_person`
- `state`: Estado da tarefa para efeitos de filtro: `NEW` ...
- `limit`: Número de registros desejados, por default 50
- `last_task_id`: Último `task_id` retornado para efeitos de paginação

**Resposta:**

`200 - OK`

```json
{
    "data": [
        {
            "company": "alelo",
            "task_id": "013d78ef-6034-4e74-8b4c-670ceccce2e4", 
            "task": {
                "type": "survey",
                "category": "in_person",
                "name": "PAT"
            },
            "address": {
            	"city": "Osasco",    
                "state": "SP"
            },
            "state": {
                "state": "NEW",
                "status": "WAITING",
            	"lot_reference": "17/06/2019 - SOFIE"
            }
         }
    ],
    "last_key": "013d78ef-6034-4e74-8b4c-670ceccce2e4"
}
```



## Recuperar uma tarefa específica

Objetiva recuperar todo o detalhamento de uma micro tarefa, incluindo sua eventual execução.



#### API

**Host:** https://p2hn9po6p1.execute-api.us-east-1.amazonaws.com/alpha

**Requisição:**

`GET /micro_task/management/{task_id}`

**Resposta:**

`200 - OK`

```json
{
    "company": "alelo",
    "task_id": "013d78ef-6034-4e74-8b4c-670ceccce2e4",
    "status": {
    	"when": "2019-07-11T16:34:27.217382",
    	"state": "NEW",
    	"status": "WAITING",
    	"lot_reference": "17/06/2019 - SOFIE",
    	"row_line": 2
	},
    "sofie_place": {
        "name": "SUPERMERCADO AROMA",
        "responsible": "NERIS FABRETTI",
    	"location": {
        	"lat": -23.5725951,
        	"lng": -46.7933088
    	}	        
    },
    "address": {
        "postal_code": "06045080",
        "type": "Rua",
        "full_name": "Jesuíno Antônio",
        "number": "276",
        "complement": "",
        "reference": "",
        "district": "Novo Osasco",
        "city": "Osasco",
        "state": "SP",
        "country": "BRASIL",
        "formatted_address": "Rua Jesuíno Antônio, 276 - Novo Osasco, Osasco"
    },
    "original": {
        "NU_SO_EC": "1000457157",
        "CNPJ": "1.287.759.000.160",
        "RAZAO_SOCIAL": "MERCADINHO AROMA LTDA",
        "NOME_FANTASIA": "SUPERMERCADO AROMA",
        "ENDEREÇO": "R JESUINO ANTONIO 276",
        "COMPLEMENTO_ENDERECO": "JD NOVO OSASCO",
        "CIDADE": "OSASCO",
        "UF": "SP",
        "CEP": "6045080",
        "DDD_01": "11",
        "FONE_01": "35912518",
        "FONE_02": "73520857",
        "PROPRIETARIO_01": "NERIS FABRETTI",
        "MCC": "5411",
        "DESCRICAO_MCC": "Mercearias e Supermercados",
        "VISITA SOLICITADA EM": "17/06/2019 - SOFIE"    
    }
}
```

------

`404 - NOT FOUND` - Indica que não foi encontrado um recurso de TASK_ID pelo código informado.