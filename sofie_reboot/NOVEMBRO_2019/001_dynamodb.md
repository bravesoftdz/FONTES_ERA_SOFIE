# AWS DynamoDB

Lista-se aqui as **7 tabelas** que compõe a plataforma Sofie.



##  table_sofier_info 

Armazena os dados cadastrais dos *sofiers* bem como suas configurações gerais.

| Partição | Classificação | WCU  | RCU  |
| -------- | ------------- | ---- | ---- |
| `sofier` | -             | 5    | 5    |

**Modelagem:**

```javascript
{
    "sofier": string/email, // ID do sofier
    "when": string/isoformat, // Data de cadastramento do sofier
    "birthday": string/isoformat, // Data de nascimento
	"document": string, // CPF do sofier
    "full_name": string, // Nome completo do sofier
    "main_phone": string, // Telefone principal
    "short_name": string, // Nome curto
    "bank_checking_account": {
		"account": string, // Número da conta 
        "account_digit": string, // Dígito da conta
        "account_type": string/enum, // conta_corrente
        "agency": string, // Número da agência
        "code": string, // Código do banco
        "name": string, // Nome do banco
    } // Dados bancários do sofier
}
```



## table_micro_task_flows 

Armazena as tarefas oferecidas pelo sistema bem como o seu **fluxo de execução**.

| Partição | Classificação | WCU  | RCU  |
| -------- | ------------- | ---- | ---- |
| `name`   | `version`     | 5    | 5    |

**Modelagem:**

```javascript
{
	"name": string, // Nome da tarefa
	"version": number/integer, // Versão do fluxo da execução    
    "category": string, // Categoria da tarefa
    "type": string, // Tipo da tarefa
    "alias": string, // Nome de apresentação da tarefa
    "url_thumbnails": string, // URL da imagem estática do vídeo
    "url_video": string, // URL do vídeo
    "lack_days": number/integer, // Dias de carência
    "reward": number/integer, //
    "description": string, // 
    "task_flow": [
    
    ] // Lista com o fluxo de execução da tarefa
}
```



## table_micro_task_in_person 

Armazena o backlog das tarefas a serem executadas.

| Partição  | Classificação | WCU  | RCU  |
| --------- | ------------- | ---- | ---- |
| `task_id` | -             | 25   | 25   |

**Modelagem:**

```javascript
{
	"task_id": string/uuid, // ID da tarefa
    "company": string, // ID da empresa parceira a qual se refere a tarefa
    "status": {
		"lot_reference": string, // Referência à origem da tarefa
        "row_line": number/integer, // Referência ao número da linha
        "state": string/enum, // Estado da tarefa
        "status": string/enum, // Status da tarefa em relação ao status
        "when": string/isoformat // Data de criação da tarefa
    }, // Dados referentes ao status da tarefa
    "variables": {
        
    }, // Variáveis globais à execução da tarefa 
    "last_movement": string/isoformat, // Data da última movimentação
    "sofie_place": {
        "location": {
            "lat": number/float, // Latitude
            "lng": number/float  // Longitude
        }, // Geolocalização do local
        "name": string, // Nome do estabelecimento ou outra referência similar
        "responsible": string // Nome da pessoa responsável pelo estabelecimento
    }, // Dados da localidade a ser visitada
    "address": {
        "city": string, // Nome da cidade
        "complement": string, // Complemento
        "country": string, // Nome do país (BRASIL)
        "district": string, // Nome do bairro
        "formatted_address": string, // Endereço formatado
        "full_name": string, // Nome do logradouro
        "number": string, // Número 
        "postal_code": string, // CEP - Código de Endereçamento Postal
        "reference": string, //Referência
        "state": string, // Unidade da Federação (abreviado, e.g. SP)
        "type": string // Tipo do logradouro, e.g. Avenida
    }, // Informações finais referente ao endereço
    "task": {
        "name": string, // ID da tarefa
        "category": string/enum, // Categoria da tarefa
        "type": string/enum, // Tipo da tarefa 
        "reward": number/float, // Prêmio ao sofier
    },
    "pre_preparation_address": {
        "city": string, // Nome da cidade
        "complement": string, // Complemento
        "country": string, // Nome do país (BRASIL)
        "district": string, // Nome do bairro
        "formatted_address": string, // Endereço formatado
        "full_name": string, // Nome do logradouro
        "number": string, // Número 
        "postal_code": string, // CEP - Código de Endereçamento Postal
        "reference": string, //Referência
        "state": string, // Unidade da Federação (abreviado, e.g. SP)
        "type": string // Tipo do logradouro, e.g. Avenida
    }, // Dados referentes ao endereço após a higienização dos dados recebidos
    "original": {
        
    }, // Dados originais recebidos pela empresa parceira
    "correios": {
        
    }, // Dados coletados na API dos correios
    "google_maps": {
        
    }, // Dados coletados na API do Google Maps
 	"receita_ws": {
        
    }, // Dados coletados na API intermediária à Receita Federal   
}
```



##  table_micro_task_execution 

Armazena as informações sobre a **execução** das tarefas.

Ou seja, cada vez que uma tarefa é executada os dados desta execução é registrado aqui.

| Partição  | Classificação  | WCU  | RCU  |
| --------- | -------------- | ---- | ---- |
| `task_id` | `execution_id` | 5    | 5    |

**Modelagem:**

```javascript
{
    "execution_id": string/uuid, // ID da execução 
    "task_id": string/uuid, // ID da tarefa a que se refere a execução
    "execution": [
        
    ], // Lista com o fluxo da execução
    "location": {
        "acc": number/float, // Acuracidade dos dados
        "alt": number/float, // Altitude
        "lat": number/float, // Latitude
        "lng": number/float  // Longitude
    }, // Geolocalização da execução da tarefa 
    "nps_sofier": {
        "nps": number/enum, // Nota de 1 à 5
        "style": "internal:nps"
    }, // NPS da execução da tarefa dada pelo sofier 
    "result": "string/enum", // POSTPONE indica que a tarefa foi adiada enquanto que FINISH indica que a tarefa foi executada até o fim
    "task_info": {
        "name": string, // Nome da tarefa 
        "version": number // Versão do fluxo de execução da tarefa
    }, // Informações relevantes sobre a tarefa
    "when": {
        "start": string/isoformat, // Data e hora de início da execução 
        "finish": string/isoformat // Data e hora do fim de execução
    }, // Data de início e fim da execução da tarefa
    "who": string/email, // ID do sofier
    "audit": {
        "approved": boolean, // Indica se a exeução foi aprovada ou não
        "reason": string, // Observações gerais sobre a avaliação
        "when": string/isoformat, // Data e hora da avaliação
        "who": string/email // ID do avaliador
    }, // Dados referente à auditoria
}
```



##  table_sofier_ledger 

Armazena a movimentação financeira dos *sofiers*.

> **Importante:** A modelagem está incongruente pois houve conflito na hora de registrar o débito. Portanto há duas modelagens parecidas e as informações devem ser interpretadas conforme o contexto.
>
> `reward` positivo indica movimentação de crédito
> `reward` negativo indica movimentação de débito



| Partição | Classificação  | WCU  | RCU  |
| -------- | -------------- | ---- | ---- |
| `sofier` | `execution_id` | 5    | 5    |

**Modelagem:**

*Modelagem de um crédito:*

```javascript
{
	"sofier": string/email, // ID do sofier a qual pertence a movimentação
    "execution_id": string/uuid, // ID da execução
    "task_id": string/uuid, // ID da tarefa
    "phase": string/enum, // Fase em que se encontra o movimentação
    "reward": number/float, // Prêmio da execução da tarefa
    "first_move": string/isoformat, // Data da primeira movimentação
    "last_move": string/isoformat, // Data da última movimentação
    "task_info": {
    	"name":  string, // Nome da tarefa
        "category": string, // Categoria da tarefa
        "type": string // Tipo da tarefa
    },
    "sofie_place": {
        "name": string // Nome do estabelecimento ou informação similar
    }, // Dados do estabelecimento
    "history": [
        {
			"phase": string, // Nome da fase
            "time_stamp": string/isoformat // Data em que passou para a fase
        }
    ], // Histórico da movimentação
    
}
```

*Modelagem de um débito:*

```javascript
{
	"sofier": string/email, // ID do sofier a qual pertence a movimentação
	"execution_id": string/uuid, // ID da movimentação
    "last_move": string/isoformat, // Data da última movimentação
    "phase": "AVAILABLE", // Fase em que se encontra o movimentação
    "reward": number/float, // Valor do resgate
	"sofie_place": {
        "name": "Solicitação de saque" // Descrição da movimentação
    }, // Informações sobre o saque
    "comments": string // Observações gerais
}
```



## table_support_ticket 

Armazena os tickets de suporte.

| Partição | Classificação | WCU  | RCU  |
| -------- | ------------- | ---- | ---- |
| `sofier` | `ticket_id`   | 5    | 5    |

**Modelagem:**

```javascript
{
	"sofier": string/email, // ID do sofier
    "ticket_id": string/uuid, // ID do ticket
    "status": string/enum, // Status em que se encontra o tratamento
    "when": string/isoformat, // Data da abertura do ticket
    "content": string, // Mensagem propriamente dita em relação ao ticket
    "backoffice": {
        "when": string/isoformat,  // Data em que o ticket foi colocado em tratamento
        "who": string/email // ID da pessoa que colocou o ticket em tratamento
    }, // Dados do backoffice que colocou o ticket em andamento
    "conclusion": {
    	"content": string, // Comentários quanto à conclusão do ticket
        "when": string/isoformat, // Data em que o ticket foi concluído
        "who": string/email // ID da pessoa que concluiu o ticket
    } // Dados do backoffice que concluiu o ticket
}
```



##  table_training_tips 

Armazena as dicas de utilização aos sofiers.

| Partição     | Classificação | WCU  | RCU  |
| ------------ | ------------- | ---- | ---- |
| `content_id` | -             | 5    | 5    |

**Modelagem:**

```javascript
{
    "content_id": string/uuid, // ID da dica
    "title": string, // Título da dica
    "content": string, // Conteúdo da dica
    "kind": string/enum, // Tipo de dica
}
```



## table_bread_crumbs

Armazena as localizações do sofier ao acionar a funcionalidade de radar

| Partição      | Classificação | WCU  | RCU  |
| ------------- | ------------- | ---- | ---- |
| `sofier_hash` | `when`        | 5    | 5    |

**Modelagem:**

```javascript
{
    "sofier_hash": string/uuid, // ID do sofier
    "when": string/isoformat, // Data e hora da ocorrência       "location": {
        "lat": number/float, // Latitude
        "lng": number/float  // Longitude
    } // Geolocalização da execução da tarefa 
}
```
