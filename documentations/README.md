[TOC]

# integrations

Documentação das integrações com terceiros


## CONTAINERS

**SERVIDOR FÍSICO:** 172.30.1.20
**SENHA DO ROOT:** 50f16@4dm1n

### COMANDOS PARA ATUALIZAÇÃO

```txt
docker ps
docker attach brains_blue
docker attach microservices_blue
docker attach microservice_blue2
cd /usr/local/bin/
git pull
rcbrain_web_1 restart && rcbrain_web_2 restart && rcbrain_api_1 restart && rcbrain_api_2 restart && rcbrain_api_3 restart
rcledger restart && rcclear_sale restart && rcmicro_contract restart && rcpayment restart 
```
### COMANDOS PARA RESOLVER O PROBLEMA DO gmail/token.json

```txt
git checkout the_3rd/gmail/token.json
```


## SERVIDORES

-----------------------------------------------------------------------------------------------------------------------------------------------------------------
| **Componente**    | **Artefato**  | **Host**                    | **Usuário**   | **Senha**    | **Gestão**                       | **Usuário** | **Senha**   |
|-------------------|---------------|-----------------------------|---------------|--------------|----------------------------------|-------------|-------------|
| **Cache**         | REDIS         | -h 172.30.1.20 -p 5051      |               |              | -                                |             |             |
| **Session**       | REDIS         | -h 172.30.1.20 -p 5052      |               |              | -                                |             |             |
| **Relations**     | Neo4J         | bolt://172.30.1.20:7687     | neo4j         | sofie@admin  | http://172.30.1.20:7474/browser/ |             |             |
| **Cortex**        | RabbitMQ      | amqp://172.30.1.20:5672     |               |              | http://172.30.1.20:8082/         | guest       | guest       |
| **Config**        | MongoDB       | mongodb://172.30.1.20:50102 | worker        | worker@sofie | -                                |             |             |
-----------------------------------------------------------------------------------------------------------------------------------------------------------------

## ACESSO À AWS-SOFIE

--------------------------------------------------------------------------
|  **Informação**    | **Valor**                                         |
| -----------------: | ------------------------------------------------- |
|            **URL** | https://sofie-cloud.signin.aws.amazon.com/console |
|   **Usuário Raiz** | erik@mysofie.com                                  |
| **Usuário Gestor** | mario.guedes                                      |
--------------------------------------------------------------------------

## ACESSO AO SWAGGER HUB

--------------------------------------------------------------------------
|  **Informação**    | **Valor**                                         |
| -----------------: | ------------------------------------------------- |
|       **Usuário:** | mysofie                                           |
|        **e-Mail:** | developer@mysofie.com                             |
|         **Senha:** | QMo{1rgsxtJc                                      |
--------------------------------------------------------------------------


## ACESSO AO G-SUITE MYSOFIE 

----------------------------------------------------------------------
| **Informação**   | **Valor**                                       |
|-----------------:|-------------------------------------------------|
| **G-Suite**      | **G-Suite**                                     |
| **URL**          | https://gsuite.google.com.br/intl/pt-BR/        |
| **Usuário**      | sofie@mysofie.com                               |
| **Senha**        | assistente@mysofie                              |
----------------------------------------------------------------------

## PROCESSO DE ENVIO DE E-MAIL 

-------------------------------------------------------------------------------------------------
| **Informação**    | **Valor**                                                                 |
|------------------:|---------------------------------------------------------------------------|
| **Plataforma**    | **GMail**                                                                 |
| **URL**           | https://developers.google.com/gmail/api/?hl=pt                            |
| **Projeto**       | NotificacaoAssistenteSofie - notificacaoassistentesofie                   |
| **Usuário**       | **sofie@mysofie.com**                                                     |
| **Client ID**     | 1095859954117-24kbcs65hicja47jruptlbcf78v5vi6j.apps.googleusercontent.com |
| **Client Secret** | yPZCIVGUVSepPQcULpvLRymt                                                  |
-------------------------------------------------------------------------------------------------

## PROCESSO DE MAPA ESTÁTICO & GEOCODING

------------------------------------------------------------------------------------------------
| **Informação**    | **Valor**                                                                |
|------------------:|--------------------------------------------------------------------------|
| **Plataforma**    | Google Maps Platform                                                     |
| **Projeto**       | -                                                                        |
| **API KEY**       | -                                                                        |
------------------------------------------------------------------------------------------------

## PROCESSO DE ENVIO DE SMS 

------------------------------------------------------------------------------------------------
| **Informação**    | **Valor**                                                                |
|------------------:|--------------------------------------------------------------------------|
| **Plataforma**    | **Zenvia**                                                               |
--------------------|---------------------------------------------------------------------------
| **Gestão**        | https://connect.zenvia360.com/manager/                                   | 
| **Conta**         | g4.web                                                                   |
| **Senha**         | Solutions@g4                                                             |
| **Gestor**        | ailton.vinicius@g4solutions.com.br                                       |
--------------------|---------------------------------------------------------------------------
| **API**           | https://api-rest.zenvia.com/services                                     | 
| **Conta**         | g4                                                                       | 
| **Senha**         | RXZUQFY6Sy                                                               | 
------------------------------------------------------------------------------------------------

## PROCESSO DE PAGAMENTO CIELO 

-----------------------------------------------------------------------------------------------------
| **Informação**       | **Valor**                                                                  |
|---------------------:|----------------------------------------------------------------------------|
| **Plataforma**       | **Cielo**                                                                  |
| **Estabelecimento**  | 11.04.02.28.15                                                             |
-----------------------|----------------------------------------------------------------------------|
| **_SUPORTE 24h_**    |                                                                            |
| **Telefone**         | 4002-9700                                                                  |
| **eMail**            | cieloeCommerce@cielo.com.br                                                |
-----------------------|----------------------------------------------------------------------------|
| **_PRODUÇÃO_**       |                                                                            |
| **Merchant ID**      | 10cfbea6-7ba9-46ad-8500-e03560fd015c                                       |
| **Merchant Key**     | Yt8g9zfhBIIR46fChldmREIxapaadASF2gVK0mn9                                   |
-----------------------|----------------------------------------------------------------------------|
| **_SANDBOX_**        |                                                                            | 
| **Merchant ID**      | 5f8b7ad9-8ecd-41b0-b9fa-76c78f1faefe                                       |
| **Merchant Key**     | UZTOVFUZIHITGVSCWQWFHFDCCIJDXDSUOOPCCBYW                                   |
-----------------------|-----------------------------------------------------------------------------
| **API**              | https://developercielo.github.io/Webservice-3.0/#integração-webservice-3.0 | 
| **SDK**              | https://github.com/DeveloperCielo/API-3.0-Python                           |
-----------------------------------------------------------------------------------------------------

## FRAUD PREVENTION - CLEARSALE 

-------------------------------------------------------------------------
| **Informação**    | **Valor**                                         |
|------------------:|---------------------------------------------------|
| **API**           | http://api.clearsale.com.br/docs/mobile-trust     |
--------------------|---------------------------------------------------|
| **_PRODUÇÃO_**    |                                                   | 
| **Conta**         | Sofie                                             | 
| **Senha**         | on0HAjkeyR                                        | 
-------------------------------------------------------------------------

## Analytics Mobile / CrashAnalytics - Google Firebase

---------------------------------------------------------------------------------------------------
| **Informação**          | **Valor**                                                             |
|------------------------:|-----------------------------------------------------------------------|
| **Plataforma**          | **Google Firebase Console**                                           |
| **URL**                 | https://console.firebase.google.com/u/0/project/mysofie-sofier-104b8  |
| **Usuário**             | developer@mysofie                                                     |
| **Projeto**             | MySofie-Sofier                                                        |
| **Código**              | mysofie-sofier                                                        |
| **Chave de API da Web** | AIzaSyBnfPMsULIfFmMNpSaRkjcYHlJI0b47348                               |
---------------------------------------------------------------------------------------------------

## Fabric.io - CrashAnalytics de Integração com Google Firebase

--------------------------------------------------------------------------------------
| **Informação**          | **Valor**                                                |
|------------------------:|----------------------------------------------------------|
| **Plataforma**          | **Fabric.io**                                            |
| **URL**                 | fabric.io/sofie-tecnologia                               |
| **Usuário**             | developer@mysofie.com                                    |
| **Senha**               | developer@mysofie                                        |
--------------------------------------------------------------------------------------

## Power BI - 

--------------------------------------------------------------------------------------
| **Informação**          | **Valor**                                                |
|------------------------:|----------------------------------------------------------|
| **Plataforma**          | **Power BI**                                             |
| **URL**                 | https://app.powerbi.com/groups/me/list/dashboards        |
| **Usuário**             | developer@mysofielabs.com                                |
| **Senha**               | Dev@mysofie                                              |
| **ClientID**            | f9ad81ca-ffc5-4eae-92e1-92822f9b66f1                     |
--------------------------------------------------------------------------------------

## GOOGLE PLAY CONSOLE

--------------------------------------------------------------------------------------
| **Informação**          | **Valor**                                                |
|------------------------:|----------------------------------------------------------|
| **Plataforma**          | **Google Play Console**                                  |
| **URL**                 | https://play.google.com/apps/publish/                    |
| **Usuário**             | developer@mysofie.com                                    |
| **Senha**               | developer@mysofie                                        |
--------------------------------------------------------------------------------------

## GOOGLE ANALYTICS

--------------------------------------------------------------------------------------
| **Informação**          | **Valor**                                                |
|------------------------:|----------------------------------------------------------|
| **Plataforma**          | **Google Analytics**                                     |
| **URL**                 | https://analytics.google.com                             |
| **Usuário**             | developer@mysofie.com                                    |
| **Senha**               | developer@mysofie                                        |
--------------------------------------------------------------------------------------

## GOOGLE YOUTUBE 

--------------------------------------------------------------------------------------
| **Informação**          | **Valor**                                                |
|------------------------:|----------------------------------------------------------|
| **Plataforma**          | **Google Youtube**                                       |
| **URL**                 | https://youtube.com/                                     |
| **Usuário**             | sofie@mysofie.com                                        |
| **Senha**               | assistente@mysofie                                       |
--------------------------------------------------------------------------------------

## GET RESPONSE

--------------------------------------------------------------------------------------
| **Informação**          | **Valor**                                                |
|------------------------:|----------------------------------------------------------|
| **Plataforma**          | **GET RESPONSE**                                         |
| **URL**                 | http://getresponse.pt/                                   |
| **Usuário**             | marketing@mysofie.com                                    |
| **Senha**               | Marketing@mysofie19                                      |
--------------------------------------------------------------------------------------

## PARÂMETROS DE EXECUÇÃO DOS ARTEFATOS:

**PRODUÇÃO:**
--config mongodb://172.30.1.20:50102 --caching 172.30.1.20:5051 --session 172.30.1.20:5052 --relation bolt://172.30.1.20:7687 --cortex amqp://172.30.1.20:5672

**DESENVOLVIMENTO:**
--manifest "C:\fontes_SoFIE\api_rest\manifesto.py" --config "mongodb://localhost:64500" --caching "localhost:6379" --session "localhost:6379" --relation "bolt://localhost:7687" --cortex "amqp://127.0.0.1:5672"

## CÓDIGO DE INDICAÇÃO:

----------------------------------------------------------------------------------------------------------------------------
| **REPRESENTANTE**         | **INF.**      | **COD.**      | **DISPOSITIVO** |  **LOCAL**                                 |
|---------------------------|----------------|--------------|-----------------|---------------------------------------------|
| **SOFIERs**               |                |              |                 |                                            |
| Eduardo Brasil            |                |              |                 |                                            |
| Jorge                     |                |              |                 |                                            |
| **CARAS**                 |                |              |                 |                                            |
| Banner Insterstitial      | 300x450        | CBI          |                 |                                            |
| Billboard                 | 970x250        | CBA          |                 |                                            |
| Retangulo                 | 300x250        | CRA          |                 |                                            |
| Half page                 | 300x500        | CHP          |                 |                                            |
| Banner site               | 300x150        | CSA          |                 |                                            |
| Banner estático/fixo      | 670x80         | CSB          |  DESKTOP        | caras.uol.com.br ; anamaria.uol.com.br     |
| Banner rotativo/mobile    | 300x50         | CSC          |  MOBILE         | caras.uol.com.br ; anamaria.uol.com.br     |
| Banner Facebook           | 1200x628       | CFA          |                 |                                            |
| Banner Facebook           | 1200x628       | CFB          |                 |                                            |
| Instagram                 | 1080x1920      | CIA          |                 |                                            |
| Instagram Stories         |                | CIB          |                 |                                            |
----------------------------------------------------------------------------------------------------------------------------
