"""
Your module description
"""

from botocore.vendored import requests as requests


URL = 'https://mysofie.com/api/v2/micro_task/reserve/'

HEADERS = {'Authorization': 'Bearer RVVfU09VX0FfTEVOREE='}


def get_reserveds(**kwargs) -> dict:
    """"
    
    """
    fields = [
        'task_id', 'sofier', 'name', 'address', 'booked_on'
    ]
    
    kwargs['sofier'] = '*'
    response = requests.get(URL, headers=HEADERS, params=kwargs)
    
    data = [
        {key: value for key, value in each.items() if key in fields} 
        for each in response.json().get('data', list())
    ]
    
    return fields, data
    