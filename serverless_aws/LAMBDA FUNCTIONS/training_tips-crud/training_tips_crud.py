"""
Artefatos que lidam com a tabela `table_training_tips`
"""

import boto3
from uuid import uuid1


class TraningTipsCRUD(object):
    """
    Classe de manutenção da tabela `table_training_tips`    
    """
    
    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__()
        self.__table = boto3.resource('dynamodb').Table('table_training_tips')

    def listing(self):
        """
        Recupera a listagem de Dicas do Dia
        """
        list_tips = list()
        
        params = dict()
        while True:
            response = self.__table.scan(**params)
            
            if len(response.get('Items')) > 0:
                list_tips.extend(response.get('Items'))
                
            last_key = response.get('LastEvaluatedKey')
            if not last_key:
                break
            
            params['ExclusiveStartKey'] = last_key

        return {'data': list_tips}
    
    def item(self, content_id: str): 
        """
        Recupera um item específico de Dica do Dia
        """
        params = dict(
            Key={'content_id': content_id}
        )
        response = self.__table.get_item(**params)

        return response.get('Item')
        
    def next_tip(self, previous_content_id: str) -> dict:
        """
        Recupera a próxima dica baseando-se no ID de uma anterior. 

        - Caso seja requerido a primeira dica, passa-se a constante `FIRST`
        - Se `previous_content_id` se referir à última dica, será mostrada a primeira
        """
        params = dict(Limit=1)
        
        if previous_content_id != 'FIRST':
            params['ExclusiveStartKey'] = {'content_id': previous_content_id}
        
        response = self.__table.scan(**params)
        
        if len(response['Items']) > 0:
            return response['Items'][0]
            
        else:
            return self.next_tip('FIRST')

    def create_tip(self, content: dict) -> dict: 
        """
        Insere um novo item na tabela
        """
        content['content_id'] = str(uuid1())
        self.__table.put_item(Item=content)
        
        return content
        
    def edit_tip(self, content: dict) -> dict:
        """
        Edita um 
        """
        self.__table.put_item(Item=content)
        
        return content

    def delete_tip(self, content_id: str):
        """
        Exclui um determinado item
        """
        self.__table.delete_item(Key={'content_id': content_id})
        