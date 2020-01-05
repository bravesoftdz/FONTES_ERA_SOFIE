# backend_apps

**Plataforma MySofie**

Aqui temos toda a plataforma _MySofie_ no que tange especificamente à Regras de Negócio. A árvore de diretórios segue a seguinte estrutura:

```
\...> apps  
|      \...> [NOME DE UM ASSUNTO]  
|              \...> crud.py  
|              \...> handlers.py  
|  
\...> library  
      \...> *  
```

## Arquitetura alto nível da plataforma 

### Storages

A plataforma possui os seguintes storages:

- **Config:** Baseado no **MongoDB** conterá todos os cadastros dos recursos da plataforma. Esses cadastros estarão em um 
database denominado **`config`**

- **Caching:** Baseado no **REDIS** conterá o cacheamento dos recursos da plataforma. 

- **Relation:** Baseado no **Neo4J** conterá as relações entre os recursos da plataforma, como por exemplo produtos x _sofiers_


## Parâmetros de linha de comando adicionais

Para o pleno funcionamento dos recursos deste repositório espera-se os seguintes parâmetros em linha de comando:

-----------------------------------------------------------------------------------------------------
| Parâmetro       | Propósito                              | Exemplo                   | Artefato   |
|:----------------|----------------------------------------|---------------------------|------------|
| -o / --config   | Storage de configuração da plataforma  | mongodb://localhost:64500 | MongoDB    |
| -c / --caching  | Storage de cacheamento server-side     | localhost:6379            | REDIS      |
| -s / --session  | Storage de gestão de sessão            | localhost:6379            | REDIS      |
| -r / --relation | Storage de relações entre os recursos  | bolt://127.0.0.1:7687     | Neo4J      |
| -x / --cortex   | Storage de mensageria                  | amqp://127.0.0.1:5672     | RabbitMQ   |
-----------------------------------------------------------------------------------------------------

## Classes de recursos 

---------------------------------------------------------------------------------------------
| Classe         | Propósito                             | MongoDB         | Neo4J          |
|:---------------|---------------------------------------|-----------------|----------------|
| Empresa        | Cadastro das empresas contratantes    | company         | COMPANY        | 
| Usuário        | Cadastro de usuários administrativos  | user            | USER           |
| Sofier         | Cadastro dos _sofiers_                | sofier          | SOFIER         |
| Consumidor     | Cadastro de consumidores finais       | consumer        | CONSUMER       |
| Endereço       | Cadastro de endereço                  | address         | ADDRESS        | 
| Card           | Cadastro de cards                     | card            | CARD           |
| Treinamento    | Cadastro de treinamento               | training        | TRAINING       |
| Micro contrato | Cadastro de micro contrato            | micro_contract  | MICRO_CONTRACT |
| Transação      | **Registro** das transações           | transaction     | TRANSACTION    |
---------------------------------------------------------------------------------------------

### Relacionamentos entre as classes de recurso

-------------------------------------------------------------------------------------------------------------------------------
| CLASSE       | RELAÇÃO      | CLASSE       | REPRESENTAÇÃO                          | TRADUÇÃO                              |
|:------------:|:------------:|:------------:|----------------------------------------|---------------------------------------|
| COMPANY      | AVAILABLE    | TRAINING     | `(:COMPANY)-[:AVAILABLE]->(:TRAINING)` | EMPRESA **DISPONIBILIZA** TREINAMENTO |
| COMPANY      | OFFER        | CARD         | `(:COMPANY)-[:OFFER]->(:CARD)`         | EMPRESA **OFERECE** CARD              | 
| SOFIER       | KNOW         | CARD         | `(:SOFIER)-[:KNOW]->(:CARD)`           | SOFIER **CONHECE** CARD               |                   
| SOFIER       | REGISTERED   | CONSUMER     | `(:SOFIER)-[:REGISTERED]->(:CONSUMER)` | SOFIER **CADASTROU** CONSUMIDOR       |    
| SOFIER       | REGISTERED   | ADDRESS      | `(:SOFIER)-[:REGISTERED]->(:ADDRESS)`  | SOFIER **CADASTROU** ENDEREÇO         |     
| ADDRESS      | PERTENCE     | CONSUMER     | `(ADDRESS)-[:PERTENCE]->(CONSUMER)`    | ENDEREÇO **PERTENCE** CONSUMIDOR      |           
-------------------------------------------------------------------------------------------------------------------------------

## API REST Básica

A API REST da plataforma _MySofie_ foi concebida focando, essencialmente, nas restrições e oportunidades que a plataforma
mobile nos impõe, em especial no cenário brasileiro. Isso influencia especialmente no formato dos dados trafegados.

A API REST da plataforma MySofie tem os seguintes preceitos básicos:

### Versionamento:

O versionamento da API é identificada pela raiz `/api/v1` sendo que logo em seguida vem o nome da classe do recurso.

### Recuperação de um recurso

A recuperação de um recurso se dará pelo par `name` do recurso em questão.

Também serão suportado os seguintes parâmetros na query string:

- **`fields`:** Lista de campos a serem projetados
  - Os campos devem ser seprados por vírgula 
  - Os campos "protegidos" como o `_id` serão desconsiderados


**Exemplo:**

```
GET api/v1/company/foobar?fields=name,idade,nascimento
```

### Listagem - Paginação, ordenação, filtro e projeção:

A ordenação e paginação se dará via query string, com as seguintes chaves:

-----------------------------------------------------------------------------------------------------------------------
| Parâmetro     | Propósito                               | Obrigatório | Default | Exemplos válidos                  |
|--------------:|-----------------------------------------|:-----------:|:-------:|------------------------------------
| **`per_page`**| Quantidade de registro por página       | Não         | 5       |                                   |
| **`page`**    | Número da página solicitada             | Não         | 1       |                                   |
| **`sort`**    | Campos e direção de ordenação           | Não         | name,ASC| name,ASC name,1 name,DESC name,-1 |
| **`filter`**  | Parâmetro de filtro                     | Não         |         | name,xpto                         |
| **`fields`**  | Lista de campos a serem projetados      | **SIM**     |         | name,idade,nascimento             |
-----------------------------------------------------------------------------------------------------------------------

**Exemplo:**

```
GET api/v1/company/?per_page=10&page=2&sort=name,ASC&fields=name,idade,nascimento
```

#### JSON padrão de Listagemn

A listagem de uma classe de recurso será feito da seguinte maneira:


```
{
  "page": int, // Número da página corrente
  "pages": int, // Quantidade total de páginas
  "count": int, // Quantidade de registro retornado
  "total": int, // Quantidade total de registros visíveis
  "data": [{}, {}, {}] // Lista com os dados retornados    
}
```

### Criação, Modificação e Exclusão de um recurso

Nos verbos **POST** e **PUT** (criação e modificação respectivamente) o nome do recurso deverá estar presente na URL e
prevalecerá sobre o par `name` eventualmente presente no documento JSON.

Por padrão o retorno não conterá a representação do recurso que sofreu a ação, priveligiando o mobile. Porém se for o caso
deve-se enviar a seguinte query string:

- **`after`:** Os valores possíveis são `yes` e `no` (default)
  - Vale todas as regras aplicáveis no `GET` 

**Exemplo:**

```
POST api/v1/company/nome_da_empresa
```

## Convenções quanto à modelagem dos dados

- Todo recurso terá um NOME, que será único na collection correspondente. Par `name` .
- Todo recurso terá uma versão. Par `version` .
- Todo recurso tem a informação de quem criou e quando. Par `__created__` .
- Todo recurso tem a informação de quem o arquivou. Par `__archived__` .
- As informações do tipo `datetime` obedecerão ao formato `ISODate`

**Exemplo**

```
{ 
    "name": str, 
    "__version__": int,
    "__created__": {
        "who": str,
        "when": datetime
    },
    "__archived__": {
        "who": str,
        "when": datetime
    } 
}
```

### Validação do esquema de dados 

No backend o fluxo básico de uma informação é:

```
MOBILE <--> NUVEM <--> NGINX <--> BRAIN <--> MySofieHTTPHandler <--> SofierCRUD <--> Storages
```

É extremamente importante utilizar as classes `SofierCRUD` pois elas possuem rotinas qua agluitnam as regras de 
negócio da plataforma MySofie.

E para garantir que os esquemas estejam sempre corretos é adequado definir os esquemas de cada objeto no módulo
`library.crud.schemes` criando elementos como o exemplo abaixo:

```python
SOFIER = SchemeObject(
    required=True,
    dict_pairs={
        'name': SchemeString(True, '\d{11}'),
        'password': SchemeString(False, '.+'),
        'short_name': SchemeString(False, '.+'),
        'full_name': SchemeString(False, '.+'),
        'email': SchemeString(True, REGEX_MAIL),
    }
)
```

Com isso, deve-se associar um validador _"root"_ à uma classe CRUD, como no exemplo abaixo:

```python
class SofierCRUD(CRUDBase):
    """
    CRUD da classe de recurso Sofier
    """
    resource_class = 'sofier'

    scheme = SOFIER
```

## Convenções quanto ao cacheamento lado servidor

> _"O processamento mais rápido é aquele que não é feito."_

Sempre que se mostrar conveniente será feito o cacheamento do resultado de um processamento no REDIS destinado a este fim.

É importante observar as seguintes convenções:

- **Sempre** determinar um TTL para a informação a fim de desonerar o REDIS
- **Sempre** codificar a invalidação de um cache (essencialmente nas operações CRUD)
- **Sempre** priorizar tipos de dados nativos ao REDIS, fazendo exceção quando realmente valer à pena
- A chave terá o seguinte padrão: `^MYSOFIE:CACHE:[^#]*#$`

## Convenções quanto à gestão de sessão de usuário

- A chave terá o seguinte padrão: `^MYSOFIE:SESSION:[^#]*#$`

## Convenções quanto à mensageria                                                
                                              
### Processamento de Micro Contrato                                              
                                                        
-------------------------------------------------------------------------------------------------------------------
| EXCHANGE                   | QUEUE                        | BIND                   | PROPÓSITO                  |
|----------------------------|------------------------------|------------------------|----------------------------|
| exchange_MICRO_CONTRACT    | queue_PROCESS_MICRO_CONTRACT | SOFIE.MICRO_CONTRACT.# | Execução de Micro Contrato |
-------------------------------------------------------------------------------------------------------------------

**Mensagens previstas:**

- `SOFIE.MICRO_CONTRACT.CREATE`
- `SOFIE.MICRO_CONTRACT.[TRANSAÇÃO].[CLÁUSULA].RUN`
- `SOFIE.MICRO_CONTRACT.[TRANSAÇÃO].STATUS`
- `SOFIE.MICRO_CONTRACT.[TRANSAÇÃO].CANCEL`

### Interação com Meios de Pagamento

-------------------------------------------------------------------------------------------------------------------
| EXCHANGE                   | QUEUE                        | BIND                   | PROPÓSITO                  |
|----------------------------|------------------------------|------------------------|----------------------------|
| exchange_PAYMENT           | queue_PAYMENT_CIELO          | PAYMENT.CIELO.#        | Processamento de Pagamento |
-------------------------------------------------------------------------------------------------------------------

**Mensagens previstas:**

- `PAYMENT.[ADQUIRENTE].[TRANSAÇÃO].QUERYBIN` - Consulta a validade do cortão de crédito
- `PAYMENT.[ADQUIRENTE].[TRANSAÇÃO].AUTHORIZATION` - Solicita a pré autorização da venda
- `PAYMENT.[ADQUIRENTE].[TRANSAÇÃO].CAPTURE` - Solicita a captura da venda
- `PAYMENT.[ADQUIRENTE].[TRANSAÇÃO].CANCEL` - Solicita o cancelamento da venda

