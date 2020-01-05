import json
import audit

def lambda_handler(event, context):
    
    task_id = event['pathParameters'].get('task_id')
    execution_id = event['pathParameters'].get('execution_id')
    
    body = json.loads(event['body'])
    
    b_ret = audit.AuditTask(task_id, execution_id, **body)()
    
    return {
        'statusCode': 200,
        'body': json.dumps({'SUCCESS': b_ret}),
        'headers': {
    	    'Access-Control-Allow-Origin': '*'    
        }         
    }
