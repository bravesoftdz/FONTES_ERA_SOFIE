# Redis Bússola



Para resolver as questões relacionadas à geolocalização usaremos o Redis e seus recursos.



## Nomeação das chaves no Redis

Nesta seção descreve-se as chaves que gerenciam todos os aspectos .

------

**CONJUNTO DE TAREFAS PRESENCIAIS:**

_As tarefas presenciais ativas são aglutinadas em uma chave geolocalizada._

`SOFIE:MICROTASK:IN_PERSON#`

------

**DADOS DE MICRO TAREFA:**

_Uma tarefa que não esteja encerrada tem os seus dados armazenados em uma chave que possui o ID da tarefa na composição do nome da chave._

`SOFIE:MICROTASK:<ID DA TAREFA>:DATA#`

------

**TAREFA NO MOSTRUÁRIO DE UM SOFIER:**

*Esta chave tem um **TTL de 3'10''** (uma vez que pretende-se mostrar a tarefa por 3 minutos na tela do sofier) e indica que a tarefa em questão está sendo oferecida a um sofier. A presença desta chave impede que a tarefa seja mostrada a outro sofier por este tempo.*

`SOFIE:MICROTASK:<ID DA TAREFA>:SHOWCASE:<ID DO SOFIER>#`

------

**TAREFA RESERVADA POR UM SOFIER:**

*Esta chave indica que uma determinada tarefa foi <u>reservada</u> à um sofier, possuindo um **TTL de 48 horas**.* 

`SOFIE:MICROTASK:<ID DA TAREFA>:RESERVED:<ID DO SOFIER>#`

------

**TAREFA REJEITADA POR UM SOFIER:**

*Esta chave indica que uma determinada tarefa foi <u>rejeitada</u> por um sofier possuindo um **TTL de 24 horas**.*

`SOFIE:MICROTASK:<ID DA TAREFA>:REJECTED:<ID DO SOFIER>#`

------

**TAREFA EM EXECUÇÃO POR UM SOFEIR:**

*Esta chave indica que uma determinada tarefa está em execução por um determinado sofier. Ela terá um TTL de três horas.* 

`SOFIE:MICROTASK:<ID DA TAREFA>:IN_EXECUTION:<ID DO SOFIER>#`

