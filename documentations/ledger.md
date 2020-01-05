# LEDGER - LIVRO RAZÃO

O **Livro Razão** é a entidade no MySofie responsável por controlar as movimentações financeiras
das partes interessadas na solução _MySofie_:

- Sofier
- Consumidor
- Empresas
- Parceiros (MarketPlace)

## Microsserviço

O microsserviço `ledger` será responsável por lidar com o Livro Razão tendo as seguintes ações:

- Criar uma Entrada
- Solicitar Balanço
- Solicitar Resgate

### Mensageria

----------------------------------------------------------------------------------------------------
| EXCHANGE        | QUEUE                | BIND           | PROPÓSITO                              |
|-----------------|----------------------|----------------|----------------------------------------|
| exchange_LEDGER | queue_PROCESS_LEDGER | SOFIE.LEDGER.# | Execução de algo relacionado ao Ledger |
----------------------------------------------------------------------------------------------------

**Mensagens previstas:**

- `SOFIE.LEDGER.ENTRY`
- `SOFIE.LEDGER.BALANCE`
- `SOFIE.LEDGER.RESCUE`

## Representações dos recursos

De uma entrada
--------------

```
{
    "name": str, // ID da entrada no livro razão 
    "part": {
        "type": "sofier"
        "id": str
    }, // Identificação da parte
    "type": ^(Cr|Dr)$, // Tipo da operação: Crédito ou Débito do ponto de vista da parte
    "transaction": str, // Referência à Transação 
    "value": number, // Valor da movimentação
    "description": str // Descrição da movimentação
}
```

Do extrato
----------

```
{
    "part": {
        "type": "sofier"
        "id": str
    }, // Identificação da parte
    
    "balance": {
        "date": ISODate
        "final_balance": number,
    }, // Balanço do momento
    
    "movement": [
        {
            "type": ^(Cr|Dr)$, // Tipo de movimentação - Débito ou Crédito 
            "value": number, // Valor da movimentação
            "date": ISODate, // Data da movimentação
            "description": str // Descrição da movimentação
        }
    ], // Movimentação ordenado por data decrescente
}
```