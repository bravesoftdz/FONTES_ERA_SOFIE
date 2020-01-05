import json

VERSION = '1.0.3-191109'
MAINTENANCE = False
URL_BASE = 'https://p2hn9po6p1.execute-api.us-east-1.amazonaws.com/alpha'
LIST_TESTERS = [
    "thiago.filadelfo@gmail.com",  
    "thiago@arrayof.io", 
    "sonia@mysofie.com", 
    "mario.guedes@mysofie.com", 
    "mario@arrayof.io", 
    "erik@mysofie.com", 
    "felipe.felix@mysofie.com",
    "jmarioguedes@gmail.com",
    "julio.moretti@mindbe.com.br",
    "felipe.bds2015@gmail.com"
]

data = {
    'current_version': VERSION,
    'maintenance': MAINTENANCE,
    'url_base': URL_BASE,
    'testers': LIST_TESTERS,
    's3': {
        'tasks': {
            'bucket': 'micro-tasks-sp',
            'region': 'sa-east-1'
        },
        'profile': {
            'bucket': 'sofie-assets',
            'region': 'sa-east-1'
        }
    }
}


def lambda_handler(event, context):
    
    return {
        'statusCode': 200,
        'body': json.dumps(data),
        'headers': {
    	    'Access-Control-Allow-Origin': '*'    
        }         
    }
