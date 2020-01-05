# Micro Contrato - Mecânica de Funcionamento 

:metal:

Identificamos três artefatos principais para a execução de uma transação:

## Conceitos

### 1 - Transação:

Uma Transação, `library.micro_contract.transaction.Transaction` representa a execução de um determinado **Card**.

### 2 - Micro Contrato:

O Micro Contrato terá funcionamento _similar_ ao Smart Contract do BlockChain.
Queremos com isso criar familiaridade com os conceitos inerentes ao BlockChain,

A ideia básica é termos uma classe descendente de `library.micro_contract.micro_contract.MicroContractBase` .
Esses micro contratos oferecerão métodos para enriquecer os dados da Transação bem como efetivar.

### 3 - Fluxo:

Este elemento, que não será ainda desenvolvido no MVP1, resgata as ideias do ISR onde um fluxo será desenhado e
interpretado pelo aplicativo para navegar pelos passos.

## API REST

**Criar uma nova transação**

`POST /api/v1/transaction?card=[CÓDIGO DO CARD]`

**Dar andamento a uma transação**

`PUT /api/v1/transaction/[CÓDIGO DA TRANSAÇÃO]/?contract_clause=[CLÁUSULA DO CONTRATO]`

**Consultar o status de uma transação**

`GET /api/v1/transaction/[CÓDIGO DA TRANSAÇÃO]`

**Cancelar o andamento de uma transação**

`DELETE /api/v1/transaction/[CÓDIGO DA TRANSAÇÃO]`

## FLUXO ESPECIAL PARA A EDITORA CARAS

As chamadas para as fichas da *Editora Caras* seguirão as seguintes etapas:

**:heavy_check_mark: Passo 1 - Criação da Transação**

`POST /api/v1/transaction?card=[CÓDIGO DO CARD]`

**Conteúdo:** _Sem conteúdo_

**Retorno:** `201 - CREATED`

```
{
    "transaction": str // Código da Transação
}
```

**:heavy_check_mark: Passo 2 - Definição da Condição de Pagamento**

`PUT /api/v1/transaction/[CÓDIGO DA TRANSAÇÃO]/?contract_clause=set_payment_condition` 

```
{
    "payment_condition": str // Nome da condição de pagamento escolhida
}
```

**:heavy_check_mark: Passo 3 - Definição do Consumidor**

`PUT /api/v1/transaction/[CÓDIGO DA TRANSAÇÃO]/?contract_clause=set_consumer`

```
{
    "consumer": str // Código do Consumidor cadastrado
}
```

**:heavy_check_mark: Passo 4 - Definição do Endereço de Entrega**

`PUT /api/v1/transaction/[CÓDIGO DA TRANSAÇÃO]/?contract_clause=set_address`

```
{
    "address": str // Código do Endereço Cadastrado
}
```

**:heavy_check_mark: Passo 5 - Envio do Link de Pagamento**

`PUT /api/v1/transaction/[CÓDIGO DA TRANSAÇÃO]/?contract_clause=send_payment_link`

```
{
    "via": {
        "sms": bool, // Indica que é para enviar para o SMS do Consumidor
        "email": bool, // Indica que é para enviar para o email do Consumidor
        "telegram": bool, // Indica que é para enviar para o Telegram do Consumidor - NÃO SUPORTADO
        "facebook": bool, // Indica que é para enviar para o Facebook do Consumdor - NÃO SUPORTADO
        "whatsapp": bool, // Indica que é para enviar para o WhatsApp do Consumidor - NÃO SUPORTADO
    }
}
```

**:heavy_check_mark: Passo 6 - Cancelamento da Transação**

`DELETE /api/v1/transaction/[CÓDIGO DA TRANSAÇÃO]`


**:heavy_check_mark: Passo 7 - Status da Transação**

`GET /api/v1/transaction/[CÓDIGO DA TRANSAÇÃO]`


## Representação JSON

```
{
    "transaction" : str, // ID da transação
    "protocol": str, // Protocolo para o Consumidor
    
    "status": {
        "state": ^(QUEUED|PAUSED|PROCESSING|FINISHED)$, // Estado
        "success": bool, // Indica se houve sucesso ou não na operação
        "reason": str, // Motivo do sucesso ou insucesso
    }, // Informações sobre o status
    
    "parts": {
        "sofier": str, // ID do Sofier
        "consumer": str,  // ID do Consumidor
        "address": str, // ID do  endereço
        "card": str, // ID do Card
        "company": str, // Nome da empresa
    },
    
    "payment_condition" : {
        "reward_day" : ISODate, // Data que o valor será liberado ao Sofier
        "fee" : number, // Valor a ser repassado para a plataforma
        "method" : ^(CREDIT_CARD)$, // Meio de pagamento escolhido
        "price" : number, // Valor do Card 
        "quotes" : {
            "qtt" : number, // Quantidade de parcelas
            "value" : number, // Valor de cada parcela
            "with_rate" : bool // Indica se há juros ou não
        }, 
        "reward" : number, // Valor do prêmio a ser pago ao Sofier
        "title" : str // Título da condição de pagamento dentro do Card
    },    

    "payment_info": {
        "method": ^(CREDIT_CARD)$, // Descrição do Meio de pagamento
        "credit_card": {
            "hash": str, // Hash dos dados do Cartão para referência no Neo4J
            "acquirer": ^(CIELO)$, // Empresa adquirente
            
            "validation": {
                "valid": bool, // Indica se o cartão é válido
                "when": ISODate, // Momento da resposta da validação
                "log": [{}] // Informações sobre a validação
            }, //Pré consulta do BIN
            
            "authorization": {
                "authorized": bool, // Indica se a operação foi autorizada ou não
                "when": ISODate, // Momento da reposta da autorização
                "log": [{}], // JSONs retornados pela adquirente
            }, // Informações sobre a autorização
            
            "catch": {
                "captured": bool, // Indica se a operação foi capturada ou não
                "when": ISODate(), // Momento da reposta da captura
                "log": [{}] // JSONs retornados pela adquirente
            }, // Informações sobre a captura
            
            "cancellation": {
                "canceled": bool, // Indica se a operação foi cancelada ou não
                "when": ISODate(), // Momento da reposta do cancelamento
                "log": [{}] // JSONs retornados pela adquirente
            } // Informações sobre o cancelamento
        } // Informações pertinentes ao Cartão de Crédito
    },
    
    "udf": {
        
    }, // Dados Definidos pelo usuário esperados pelo Micro Contrato
}
```
