[TOC]

# Informações sobre a execução de uma tarefa



### Item de execução de uma micro tarefa

Recupera as informações de uma execução de tarefa.



#### API

**Requisição**:

`GET /micro_task/management/{task_id}/execution/{execution_id}`

**Resposta:**

`200 - OK`

```json
{
	"task_id": "3be9bdba-49f3-4e7d-aa91-564f11a1e9c8",
	"execution_id": "7b1824f0-bf9d-11e9-a582-ded4e857a9b5",
	"task_info": {
		"name": "PAT",
		"version": 1
	},
	"who": "thiago.filadelfo@gmail.com",
	"location": {
		"lat": -23.4950117,
		"lng": -46.79878,
		"acc": 13.522,
		"alt": 0
	},
	"when": {
		"start": "2019-08-16T15:17:06",
		"finish": "2019-08-16T15:19:10"
	},
	"nps_sofier": {
		"nps": 3,
		"comment": "ok ok",
		"label": ""
	},
	"audit": {
    	"when": "2019-07-11T16:34:27.217382",
        "who": "mario.guedes@mysofie.com",
        "approved": False,
        "reason": "Foto escura"
    },    
	"execution": [{
		"when": "2019-08-16T15:18:57",
		"response": "joia",
		"index": 9600,
		"statement": "Por fim, o responsável pelo estabelecimento deseja enviar uma mensagem à Alelo?",
		"context": "ESTABELECIMENTO:MENSAGEM"
	}]
}
```

