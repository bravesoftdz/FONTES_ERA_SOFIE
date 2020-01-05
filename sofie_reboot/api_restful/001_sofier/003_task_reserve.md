[TOC]

# Desafios Presenciais

O *sofier* <u>aceitará</u> ou <u>rejeitará</u> a execução de **desafios presenciais** que se caracterizam pela presença do *sofier* em um lugar certo e determinado para a execução de uma tarefa.

A fim de garantir "atomicidade" nas transações envolvidas neste assunto será recuperado a localidade mais próxima da localização do *sofier*.

- A tarefa tem que estar como `NEW`
- A tarefa não pode estar com nenhum outro *sofier*.
- A tarefa não pode estar reservada por nenhum outro *sofier*.

O *sofier* poderá reservar um desafio para sim e terá 48 horas para a execução.



## Reserva de Desafio Presencial

A fim de poupar recursos e agilizar os processo aglutinou-se os processos de solicitação, reserva e rejeição em uma única chamada onde os parâmetros influenciarão no comportamento da API.

### API

**Host:** https://p2hn9po6p1.execute-api.us-east-1.amazonaws.com/alpha 

**Request:**

`POST /micro_task/reserve/`

- `sofier`: E-Mail do *sofier* que será utilizado como chave de controle

- `task_id`: [opcional] ID da tarefa

- `action`: [opcional] Ação a ser executada no `task_id` passado: `accept` ou `reject`

-  `lat`: Latitude de referência

- `lng`: Longitude de referência

- `radius`: Raio de abrangência para a pesquisa

  

**Response:**

`200- OK` - Indica que a ação foi aceita foi aceita, e veio NOVO conteúdo

---

```json
{
    "task": {
    	"category": "in_person",
    	"type": "survey",
    	"task_id": "a54107a5-a499-4570-b7cd-c16efe79c9e3",
    	"reward": 10,
    	"address": "Avenida Edmundo Amaral, 3901, TERREO - Piratininga, Osasco",
    	"name": "PIZZARIA LAREIRA",
    	"lat": -23.5151076,
    	"lng": -46.8036752,
    	"distance": 0.1305,
    	"valid_until": "2019-07-17T11:37:01.889661"
    },
    "nearest": 200
}
```

---

`204 - NO CONTENT` - Indica que a ação foi aceita e NÃO veio novo conteúdo

---

`400 - BAD REQUEST` - Indica que houve um erro ao executar a ação



## Listagem de Desafios Reservados

Os desafios reservados serão listados para que o *sofier* escolha um que irá executar.

### API

**Host:** https://p2hn9po6p1.execute-api.us-east-1.amazonaws.com/alpha 

**Authorization:** "Eu sou a Lenda"

**Request:**

`GET /micro_task/reserve/`

- `sofier`: E-Mail do *sofier* que será utilizado como chave de controle

**Response:**

`200 - OK` 

```json
{
    "data": [
        {
    		"category": "in_person",
            "type": "survey",
    		"task_id": "a54107a5-a499-4570-b7cd-c16efe79c9e3",
    		"reward": 10,
    		"address": "Avenida Edmundo Amaral, 3901, TERREO - Piratininga, Osasco",
    		"name": "PIZZARIA LAREIRA",
    		"lat": -23.5151076,
    		"lng": -46.8036752,
    		"distance": 0.1305, 
            "valid_until": "2019-07-11T17:04:00.00000",
            "booked_on": "2019-07-09T17:04:00.00000"
        }
    ]
}
```



