[TOC]

# Auditoria de uma tarefa



## Execução de auditoria

API responsável por auditar uma execução de tarefa.



#### API

**Requisição**:

`POST /micro_task/management/{task_id}/execution/{execution_id}/audit`

- `task_id`: ID da tarefa
- `execution_id`: ID da execução



```json
{
    "who": "mario.guedes@mysofie.com",
    "approved": false,
    "reason": "Foto escura"
}
```



**Resposta:**

`200 - OK`



```json
{"SUCCESS": true}
```

