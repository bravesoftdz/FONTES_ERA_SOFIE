# Ciclo de Vida de uma micro tarefa



Uma micro tarefa nasce à partir de uma importação de mailing fornecido pela empresa parceira, como a Alelo por exemplo.

Nesta seção trataremos do ciclo de vida de uma micro tarefa.



## Status X State

A situação de uma micro tarefa é composto por duas informações que se complementam: *status* e *state*.

Temos as seguintes combinações:

| STATE     | STATUS    |
| --------- | --------- |
| NEW       | WAITING   |
| REJECTED  | REJECTED  |
| EXECUTED  | EXECUTED  |
| FINISHED  | SUCCSESS  |
|           | FAILURE   |
| CANCELLED | CANCELLED |



Quando uma tarefa é ==CRIADA== ela assume o *state* **NEW** ou **REJECTED**. Em caso de **REJECTED** há uma informação adicional que é *reason*, ou seja, o motivo pelo qual foi rejeitada.



Uma tarefa é considerada ==EXECUTADA== quando seu fluxo de execução é efetuado até o fim, lembrando que pode haver *n* tentativas de execução. Neste momento é criado uma entrada no extrato do *sofier* com o prêmio condicionado à auditoria.



Uma tarefa ==AUDITADA== assume o *state* **FINISHED** onde temos, então, dois *status*: **SUCCESS** e **FAILURE**.

Em caso de <u>sucesso</u>, o valor destinado ao *sofier* muda de status e passa-se a contar os dias de carência acordado com o parceiro.

Já em caso de <u>insucesso</u> teremos a informação *reason* com os motivos de rejeição.



Por fim uma tarefa pode ser ==CANCELADA==, *state* **CANCELLED**, onde teremos também a informação adicional *reason*.