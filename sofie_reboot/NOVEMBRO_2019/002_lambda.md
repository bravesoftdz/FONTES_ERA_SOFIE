# AWS Lambda

Aqui são descritas todas as funções AWS-Lambdas e suas principais características. Quando pertinente há uma referência para a API REST que gera o evento.



##  app-version

Esta função tem por objetivo *orientar* o aplicativo quanto as chamadas subsequentes.

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:03        |

Retorna as seguintes informações:

```javascript
{
    "current_version": string, // Versão atual do aplicativo
    "maintenance": boolean, // Indica se o sistema está em manutenção ou não
    "url_base": string, // URL base da API Rest da plataforma Sofie
    "testers": [string,] // Lista de emails de usuários testes
}
```



## micro_task-audit

Efetua a auditoria disparando todos os eventos decorrentes de uma aprovação ou reprovação.

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 01:00        |

==[DIAGRAMA DE EXECUÇÃO]==

Retorna a seguinte informação:

```javascript
{
	"SUCCESS": boolean // Indica se houve sucesso ou não na operação
}
```



## micro_task-dashboard

Basicamente varre toda a tabela `table_micro_task_in_person` totalizando  os `state` e `status` das tarefas presentes na tabela.

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 01:00        |

Retorna  algo parecido com:

```javascript
{
	"state": {
	
	},
	"status": {
	
	}
}
```

> **IMPORTANTE:** Esta função precisa ser revista pois tende a consumir muitos recursos e ficar lenta conforme o crescimento da tabela. Indica-se a utilização do REDIS para isso desde que este esteja no ElasticCache.

**API Rest:** https://app.swaggerhub.com/apis-docs/sofi97/Sofie/1#/dashboard/get_task_dashboard



## micro_task-execution

Têm o propósito de retornar uma listagem de execução de tarefas ou um item. Para isso lida com a tabela `table_micro_task_execution`.

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:03        |



## micro_task-finish

Têm o propósito de registrar a ***finalização*** da execução de uma determinada tarefa, disparando os eventos decorrentes.

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:10        |

==[DIAGRAMA DE EXECUÇÃO]==

Retorna a seguinte estrutura:

```javascript
{
	"message": "SUCCESS"
}
```

**API Rest:** https://app.swaggerhub.com/apis-docs/sofi97/Sofie/1#/execution_finish/execution_finish



## micro_task-flowPAT

Contêm o fluxo de execução específico ao desafio PAT da empresa parceira Alelo.

Em uma eventual mudança no fluxo de execução da tarefa este lambda deve ser modificado e acionado para registrar a nova versão do fluxo na tabela ` table_micro_task_flows `.


| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 01:00        |



##  micro_task-item

Retorna um item específico de tarefa da tabela `table_micro_task_in_person`.


| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:03        |



## micro_task-listing

Retorna uma listagem de tarefas oriundas da tabela `table_micro_task_in_person`.


| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:30        |

**API Rest:** https://app.swaggerhub.com/apis-docs/sofi97/Sofie/1#/list_micro_task/get_list_micro_task



## micro_task-markers

Retorna uma estrutura de dados aderente à plotagem de mapa com todas as coordenadas geográficas das tarefas presentes na tabela `table_micro_task_in_person`.

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:10        |

> **IMPORTANTE:** Esta função lambda se mostra em desuso e deve ser eliminada.

**API Rest:** https://app.swaggerhub.com/apis-docs/sofi97/Sofie/1#/markers/get_markers



## micro_task-radar

À partir das coordenadas passadas como parâmetro, *latitude, longitude e radio*, é repassado as coordenadas de todos os estabelecimentos possíveis no rádio passado.

> **IMPORTANTE:** Estas informações vêm do REDIS presente no servidor da Equinix

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:15        |



## micro_task-reserve

Conforme os parâmetros passados esta função tem os seguintes propósitos:

- Marcar uma determinada tarefa como *reservada* à um determinado *sofier*
- Recuperar a próxima tarefa geolocalizada mais próxima às coordenadas do *sofier*

> **IMPORTANTE:** Estas informações vêm do REDIS presente no servidor da Equinix

==[DIAGRAMA DE EXECUÇÃO]==

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:15        |



## micro_task-start

Registra a ***inicialização*** da execução de uma determinada tarefa por um determinado *sofier*, disparando os eventos decorrentes.

==[DIAGRAMA DE EXECUÇÃO]==


| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:15        |

**API REST:** https://app.swaggerhub.com/apis-docs/sofi97/Sofie/1#/execution_start/execution_start



## miscellaneous-bank

Retorna a lista de instituições financeiras suportadas pela operação Sofie. A listagem está _hard-code_ pois assim é bom o suficiente.

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:03        |



##  payment_credit_card-flow

Esta função lambda ainda não foi finalizada e está estacionada até que em algum momento seja necessário oferecer a funcionalidade de pagamento.

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 01:00        |



## sofier_info-crud

Esta função provê o CRUD na tabela `table_sofier_info`, estando previsto neste momento o *CREATE* e o *READ*.


| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:03        |



## sofier_ledger-balance

Esta função gera o balanço financeiro de um determinado *sofier*.  Para isso é varrido a tabela `table_sofier_ledger`.

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:15        |



## sofier_ledger-statement

Retorna o extrato de movimentação financeira relativa à uma determinada fase, de um determinado *sofier*.

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:15        |



## sofier_ledger-withdrawal

Efetua a solicitação de resgate do crédito disponível ao *sofier*, disparando os eventos decorrentes.

==[DIAGRAMA DE EXECUÇÃO]==

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 01:00        |



## support_ticket-flow

Responsável por todo o ciclo de vida de um ticket de suporte:
- Criação
- Andamento
- Finalização
- Listagem

==[DIAGRAMA DE EXECUÇÃO]==

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:10        |



## ticket-dashboard

Listagem dos tickets e seus status para efeitos de acompanhamento. A depender dos parâmetros retorna um dashboard ou uma listagem de acordo com o status solicitado.

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:10        |



## training_tips-crud

Responsável pelo *CRUD* em relação à tabela `table_training_tips` estando previsto as operações:

- Criação
- Edição
- Exclusão
- Recuperação de listagem
- Recuperação de item

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:30        |



## training_instructions-crud

Responsável pelo *CRUD* em relação à tabela ` table_micro_task_flows ` estando previsto as operações:

- Recuperação de listagem
- Recuperação de item

| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 00:30        |



## reports

Responsável tanta pela listagem de relatórios previstos na plataforma quanto pela geração dos mesmos.

Relatórios previstos:

- Listagem de sofiers
- Execuções por sofier


| Função IAM           | Memória | Tempo limite |
| -------------------- | ------- | ------------ |
| SofieLambdaExecution | 128 MB  | 05:00        |

