#MUDANÇAS NA API REST EM RELAÇÃO AO SOFIER

## Criação de um novo SOFIER

1. O CPF deixa de ser obrigatório
2. Deixa de ser necessário passar o ID no POST

No response virá o par `sofier_id` que deverá ser utilizado em outras chamadas no atributo que 
identifica o _sofier_.
