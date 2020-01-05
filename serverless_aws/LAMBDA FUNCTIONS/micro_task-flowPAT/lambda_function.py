import json
import flow_pat

def lambda_handler(event, context):
    
    b_ret = flow_pat.generate_flow()
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'{b_ret} - Parece que deu tudo certo')
    }
