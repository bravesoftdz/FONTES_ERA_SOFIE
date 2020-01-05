import boto3
from datetime import datetime
from botocore.vendored import requests as requests


def register_bread_crumbs(sofier: str, lat: float, lng: float, qtt: int):
    """
    
    """
    TABLE = boto3.resource('dynamodb').Table('table_bread_crumbs')
    
    if not sofier:
        sofier = 'UNKNOWN'
    
    data = {
        'sofier_hash': sofier,
        'when': datetime.utcnow().isoformat(),
        'location': {
            'lat': lat,
            'lng': lng
        },
        'qtt': qtt
    }
    
    TABLE.put_item(Item=data)


def get_radar(**kwargs):
    """
    
    """
    URL = 'https://mysofie.com/api/v2/micro_task/radar/'
    HEADERS = {'Authorization': 'Bearer RVVfU09VX0FfTEVOREE='}

    response = requests.get(URL, headers=HEADERS, params=kwargs)
    return response.status_code, response.json()    