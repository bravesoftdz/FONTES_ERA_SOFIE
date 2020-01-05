# Passagem de conhecimento

Este diretório contêm informações sobre o *status quo* do backend da plataforma Sofie para efeitos de passagem de conhecimento.

>  **IMPORTENTE:** Reflete a situação _"como está"_ em NOVEMBRO de 2019.

Os pilares desta documentação são:

---

**Recursos *serverless* da AWS** 

- :heavy_check_mark: [Tabelas do **AWS-DynamoDB**](./001_dynamodb.md)
- :heavy_check_mark: [Funções do **AWS-Lambda**](./002_lambda.md)
- [Rotas do **AWS-API Gateway**](https://app.swaggerhub.com/apis-docs/sofi97/Sofie/1)
- Arquivos do **AWS-S3**
- Configuração do **AWS- Cognito**

---

**Recursos *dedicados* no servidor Equinix**

- Funções do **Redis**
- Envio de **e-Mail via Google**

---

**Scripts de manutenção no Jupyter Notebook**

- :heavy_check_mark: [Exclusão das movimentações de teste (tarefas e pagamentos)](https://github.com/my-sofie/serverless_aws/blob/master/NOTEBOOK%20-%20ANALISES/001%20-%20EXCLUSÃO%20DOS%20TESTES.ipynb)
- Liberação de saldos *(de Aprovado para Disponível)* dos usuários *testers*

---

**Scripts de importação de tarefas especificamente da Alelo**



