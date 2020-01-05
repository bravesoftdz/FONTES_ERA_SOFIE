#######################################################################
#                                                                     #
# >> micro_task-finish <<                                             #
#                                                                     #
# Têm por proósito registrar a finalização execução de uma tarefa     #
#                                                                     #
#######################################################################

import json
import boto3
import decimal
from datetime import datetime
from botocore.vendored import requests as requests

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o) if o % 1 == 0 else float(o)

        return super(DecimalEncoder, self).default(o)


def lambda_handler(event, context):
    
    task_id = event['pathParameters'].get('task_id')
    sofier = event['queryStringParameters'].get('sofier')
    execution_data = json.loads(event['body'], parse_float=decimal.Decimal)
    
    status, data = set_finish_execution(task_id, sofier, execution_data)
    
    return {
        'statusCode': status,
        'body': json.dumps(data, cls=DecimalEncoder),
        'headers': {
            'Access-Control-Allow-Origin': '*'    
        }          
    }
    
URL = 'https://mysofie.com/api/v2/micro_task/execution/{task_id}/finish'

HEADERS = {'Authorization': 'Bearer RVVfU09VX0FfTEVOREE='}

def set_finish_execution(task_id: str, sofier: str, execution_data: dict) -> tuple:
    """
    --

    [X] - Inserção na tabela `table_micro_task_execution`
    [X] - Edição na tabela `table_micro_task_in_person`
    [X] - Chamada REST para Equinix 
    """
    status, response = 500, None

    #: Verificando se a execução da tarefa foi ADIADA, CANCELADA ou FINALIZADA
    postpone_or_cancel = 'FINISH'
    for each in execution_data['execution']:
        if each['context'] == 'SYSTEM:TASK:POSTPONE_OR_CANCEL':
            postpone_or_cancel = each['response']
            break
        
    #: Determinando o RESULTADO da execução
    execution_data['result'] = postpone_or_cancel
        
    #: Inserção na tabela `table_micro_task_execution`
    boto3.resource('dynamodb').Table('table_micro_task_execution').put_item(
        Item=execution_data,
    )

    #: Editando a tabela `table_micro_task_in_person`
    params_to_update = dict(
        Key={'task_id': task_id},    
        UpdateExpression='SET #status.#state = :s, #status.#status = :s, last_movement = :lm, #status.last_sofier = :ls',
        ExpressionAttributeNames={'#status': 'status', '#state': 'state'},
        ExpressionAttributeValues={':s': 'EXECUTED', ':lm': datetime.utcnow().isoformat(), ':ls': sofier},
        ReturnValues='ALL_NEW' 
    )

    if postpone_or_cancel == 'FINISH':
        task_info = boto3.resource('dynamodb').Table('table_micro_task_in_person').update_item(
            **params_to_update    
        )            
    
    #: Chamada REST para a Equinix finalizando a tarefa
    response = requests.post(
        URL.format(task_id=task_id), 
        headers=HEADERS, 
        params={'sofier': sofier, 'postpone_or_cancel': postpone_or_cancel}
    )
    if response.status_code != 200:
        return response.status_code, response.json()
        
    #: Efetuando o crédito na conta do *sofier* - VALIDATION
    if postpone_or_cancel == 'FINISH':
        task_info = task_info['Attributes']
        
        str_time_stamp = datetime.utcnow().isoformat()
        boto3.resource('dynamodb').Table('table_sofier_ledger').put_item(
            Item={
                'sofier': sofier,
                'execution_id': execution_data['execution_id'],
                'task_id': task_id,
                'reward': task_info['task']['reward'],
                'phase': 'VALIDATION',
                'history': [{'time_stamp': str_time_stamp, 'phase': 'VALIDATION'}],
                'last_move': str_time_stamp,
                'first_move': str_time_stamp,
                'sofie_place': {
                    'name': task_info['sofie_place']['name'],
                    'address': task_info['address']['formatted_address'] 
                },
                'task_info': {
                    'type': task_info['task']['type'],
                    'name': task_info['task']['name'],
                    'category': task_info['task']['category']
                }
            }
        )

    #: Verificando se é para enviar um email para o estabelecimento
    #TODO: CHAMADA PARA ENVIAR EMAIL

    return 200, {'message': 'SUCCESS'}
    