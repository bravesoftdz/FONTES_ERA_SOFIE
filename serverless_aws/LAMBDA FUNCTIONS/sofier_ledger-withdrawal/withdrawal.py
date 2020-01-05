from uuid import uuid1
from datetime import datetime, timedelta
from decimal import Decimal
from json import dumps

import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.vendored import requests as requests

"""

"""

class Withdrawal(object):
    """
    Executa todo o processo
    
    1) Valida de o sofier possui os dados bancários, e CPF, cadastrados
    2) Valida se o saldo disponível é maior ou igual ao valor solicitado
    3) Registra o movimento de débito na tabela `ledger`
    4) Registra a solicitação de saque e os dados na tabela `withdrawal`
    5) Envia email para:
        - rafael.rosa@mindbe.com.br 
        - erik@mysofie.com
        - sonia@mysofie.com
        - mario.guedes@mysofie.com

    O texto será parecido com o modelo:
    
        Solicitação de saque:
        
        LIMITE..: Data Limite para o depósito
        
        Nome....: Nome do sofier
        CPF.....: Número do CPF
        Valor...: Valor solicitado pelo sofier
        
        Banco...: Nome do banco
        Código..: Código do banco
        
        Tipo....: Poupança ou Corrente
        Agência.: Número da agência
        Conta...: Número da conta
        Dígito..: Dígito da conta
    
    """    
    def __init__(self, sofier: str, phase: str, value: float, reason: str):
        """
        Inicializa o objeto
        """
        super().__init__()
        self.__sofier = sofier
        self.__phase = phase
        self.__value = value
        self.__reason = reason
        self.__sofier_data = None
        self.__dt_prevision = None
        self.__table_ledger = boto3.resource('dynamodb').Table('table_sofier_ledger')
        
    def __call__(self) -> dict:
        """
        Executa todo o fluxo de saque
        """
        self.verify_sofier_data()
        self.verify_balance()
        self.make_withdrawal()
        self.send_email()
        
        return {'dt_prevision': self.__dt_prevision.isoformat()}

    def verify_sofier_data(self):
        """
        Verifica se o sofier possui os dados bancários cadastrados bem como o CPF
        """
        data = boto3.resource('dynamodb').Table('table_sofier_info').get_item(
            Key={'sofier': self.__sofier},
            ProjectionExpression='bank_checking_account, document, full_name'
        ).get('Item')
        
        if not data:
            raise Exception(f'Os dados bancários do sofier [{self.__sofier}] não foram localizados')
            
        if data['document'] is None:
            raise Exception(f'Os dados bancários do sofier [{self.__sofier}] estão incompletos')
        
        for field in ('account', 'account_digit', 'account_type', 'agency', 'code', 'name'):
            if data['bank_checking_account'][field] is None:
                raise Exception(f'Os dados bancários do sofier [{self.__sofier}] estão incompletos')
                
        self.__sofier_data = data
    
    def verify_balance(self):
        """
        Verifica o saldo do sofier que deve ser maior ou igual ao valor solicitado
        """
        balance = 0
        params = dict(
            FilterExpression=Key('sofier').eq(self.__sofier) & Attr('phase').eq(self.__phase),
        	ProjectionExpression='reward'
        )
        
        while True:
            response = self.__table_ledger.scan(**params)
            
            balance += sum([each['reward'] for each in response['Items']])
            
            last_key = response.get('LastEvaluatedKey')
            if not last_key:
                break
            params['ExclusiveStartKey'] = last_key
            
        if self.__value > balance:
            raise Exception('O saldo é insuficiente para esta operação')
    
    def make_withdrawal(self):
        """
        Registra o lançamento de débito na tabela ledger
        """
        self.__dt_prevision = datetime.utcnow() +  timedelta(days=7)
        
        self.__table_ledger.put_item(
            Item={
                'sofier': self.__sofier, 
                'execution_id': str(uuid1()),
                'reward': Decimal(-self.__value),
                'phase': 'AVAILABLE',
                'last_move': datetime.utcnow().isoformat(),
                'comments': self.__reason,
                'dt_prevision': self.__dt_prevision.isoformat()
            }
        )
    
    def send_email(self):
        """
        Solicita o envio de email aos responsáveis pelo depósito
        """
        try:
            URL = 'https://mysofie.com/api/v2/withdrawal/'
            HEADERS = {'Authorization': 'Bearer RVVfU09VX0FfTEVOREE='}
            
            data_to_email = {
                'subject': f'RESGATE SOLICITADO - {self.__sofier_data["full_name"]}',
                'to': ['rafael.rosa@mindbe.com.br', 'erik@mysofie.com', 'sonia@mysofie.com', 'mario.guedes@mysofie.com'],
                'message': self.text_to_email()
            }
            
            response = requests.post(URL, headers=HEADERS, data=dumps(data_to_email))
            
        except Exception as err:
            print('Deu erro!', err)
            
    def text_to_email(self):
        """
        Formata o email à partir dos dados passados
        """
        return (
            f'<h3>Solicitação de resgate:</h3><br/>'
            f'<strong>DATA LIMITE: {self.__dt_prevision.strftime("%d/%m/%Y")}</strong><br/><br/>'
            f'<table>'
            f'<tr><td><strong>Nome:</strong></td><td>{self.__sofier_data["full_name"]}</td></tr>'
            f'<tr><td><strong>CPF:</strong></td><td>{self.__sofier_data["document"]}</td></tr>'
            f'<tr><td><strong>Valor:</strong></td><td>R$ {self.__value:8.2f}</td></tr>'
            f'<tr><td><strong>Banco:</strong></td><td>{self.__sofier_data["bank_checking_account"]["name"]}</td></tr>'
            f'<tr><td><strong>Código:</strong></td><td>{self.__sofier_data["bank_checking_account"]["code"]}</td></tr>'
            f'<tr><td><strong>Tipo:</strong></td><td>{self.__sofier_data["bank_checking_account"]["account_type"]}</td></tr>'
            f'<tr><td><strong>Agência:</strong></td><td>{self.__sofier_data["bank_checking_account"]["agency"]}</td></tr>'
            f'<tr><td><strong>Conta:</strong></td><td>{self.__sofier_data["bank_checking_account"]["account"]} - {self.__sofier_data["bank_checking_account"]["account_digit"]}</td></tr>'
            f'</table>'
        )