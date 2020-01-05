import boto3


class SofierCRUD(object):
    """
    Operações básicas de CRUD
    """
    
    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__()
        self.__table = boto3.resource('dynamodb').Table('table_sofier_info')
        
    def listing(self):
        """
        
        """
        list_sofier = list()
        
        params = dict(
            ProjectionExpression='short_name, sofier'            
        )
        while True:
            response = self.__table.scan(**params)
            
            buffer = response.get('Items')
            if buffer:
                list_sofier.extend(buffer) 
            
            last_key = response.get('LastEvaluatedKey')
            if not last_key:
                break
            params['LastEvaluatedKey'] = last_key        
        
        return {'data': list_sofier}
    
    def put_info(self, data: dict) -> bool:
        """
        Atualiza os dados na tabela
        """
        self.__table.put_item(Item=data)
        return True
    
    def get_info(self, sofier: str) -> dict:
        """
        Retorna os dados cadastrais do _sofier
        """
        buffer = self.__table.get_item(Key={'sofier': sofier})
        
        return buffer.get('Item')
