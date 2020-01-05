[TOC]

# Execução da Tarefa

O *sofier* iniciará a execução de uma tarefa e postará a resposta final no fim da jornada.



## Início de execução de tarefa

Quando o _sofier_ iniciar a execução de uma tarefa será enviado um estímulo ao backend mudando o status da tarefa de `RESERVED` para `EXECUTING`.

O *sofier*, então, terá **três horas** para a efetiva execução da tarefa. Caso não o faça entenderemos que algo deu errado e por isso a tarefa voltará para `NEW`.



### API

**Host:** https://p2hn9po6p1.execute-api.us-east-1.amazonaws.com/alpha

**Request:**

`POST /micro_task/execution/<ID DA TAREFA>/start`

- `sofier`: Identificação do _sofier_ que é o eMail

**Response:**

`200- OK`

```json
{
    "task_id": "a54107a5-a499-4570-b7cd-c16efe79c9e3",
    "execution_id": "8754985749857458947584",
    "task_flow": [{...}, {...}], 
    "variables": {
        "produto": 47
    },
    "task_info": {
        "name": "PAT",
        "version": 1        
    }
}
```



## Envio de fotos 

Um estágio possível da execução da tarefa será o envio de uma foto.  

Para isso será alimentado um bucket S3 ao qual o **aplicativo** terá acesso e a URL final da imagem será a reposta para o estágio em questão.



## Recepção das Respostas

Quando o *sofier* finalizar uma tarefa as respostas serão enviadas ao backend que processará a solicitação de forma assíncrona.

Por isso o frontend mobile receberá apenas um status de que a solicitação foi aceita e posteriormente receberá uma notificação push, sms e email de que a resposta foi processada e está em análise.



### API

**Host:** https://p2hn9po6p1.execute-api.us-east-1.amazonaws.com/alpha

**Request:**

`POST /micro_task/execution/{task_id}/finish`

- `sofier`: Identificação do _sofier_ que é o eMail

`Content-Type: application/json`

```json
{
    "task_id": "a54107a5-a499-4570-b7cd-c16efe79c9e3",
    "execution_id": "8754985749857458947584", 
    
    "task_info": {
        "name": "PAT",
        "version": 1
    },
    
    "location": {
        "lat": -23.5656565656,
        "lng": -43.9564157
    },
        
    "who": "sofier@mysofie.com",
        
    "nps_sofier": {
    	"nps": 10,
        "comment": "Tudo lindo e maravilhoso!"
    },
        
    "when": {
        "start": "2019-08-13T20:15:00",
        "finish": "2019-08-13T45:29:00",
    },
      
    "execution": [{
        "context": "LUGAR:ERRADO:LEAD_ALELO",
        "index": 2,
        "previous": 1,
        "when": "2019-08-13T20:15:00",
        "response": "Exemplo",
    }]
}
```



**Response:**

`202 - ACCEPTED`





