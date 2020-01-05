[TOC]

# DynamoDB - Organização das Tabelas



Aqui temos a organização das tabelas do DynamoDB.



## Fluxos de Execução

**Tabela:** `table_micro_task_flows`

**Propósito:** Aqui armazenaremos os fluxos de execução das tarefas.

**Chave de Partição:**  `name`

**Chave de Classificação:** `version`



## Backlog de micro tarefas presenciais

**Tabela:** `table_micro_task_in_person`

**Propósito:** Aqui armazenaremos o backlog de tarefas presenciais.

**Chave de Partição:**  `task_id`

**Chave de Classificação:** *Não há*



## Resultado de execução de micro tarefas

**Tabela:** `table_micro_task_execution`

**Propósito:** Aqui armazenaremos as informações pertinentes à execução de uma micro tarefa.

**Chave de Partição:**  `task_id`

**Chave de Classificação:** `execution_id`



## 