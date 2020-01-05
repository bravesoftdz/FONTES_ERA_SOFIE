from collections import defaultdict
import boto3


def get_data_sofiers(sofiers: list) -> dict:
    """
    
    """
    table = boto3.resource('dynamodb').Table('table_sofier_info')
    params = dict(
        ProjectionExpression='sofier, short_name, full_name, document, bank_checking_account'
    )
    
    buffer = dict()
    while True:
        response = table.scan(**params)
        
        for each in response.get('Items'):
            if each['sofier'] in sofiers:
                buffer[each['sofier']] = each
            
        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break
        params['ExclusiveStartKey'] = last_key
        
    return buffer


def report_balance(**kwargs) -> tuple:
    """
    
    """
    fields = [
        'sofier',
        'nome',
        'resgatado',
        'análise',
        'aprovado',
        'disponível',
        'reprovado',
        'cpf',
        'modalidade',
        'banco',
        'agência',
        'conta',
    ]
    
    table = boto3.resource('dynamodb').Table('table_sofier_ledger')
    params = dict(
        ProjectionExpression='phase, reward, sofier'
    )
    FINAL = defaultdict(lambda : defaultdict(lambda : 0))
    
    while True:
        response = table.scan(**params)
        
        for each in response.get('Items'):
            sofier = each['sofier']
            phase = each['phase']
            
            FINAL[sofier][phase] += each['reward']
            
            if phase == 'AVAILABLE' and each['reward'] < 0:
                FINAL[sofier]['withdrawal'] += (each['reward'] * -1)
            
            
        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break
        params['ExclusiveStartKey'] = last_key
        
    data_sofiers = get_data_sofiers([sofier for sofier in FINAL.keys()])
    
    list_final = list()
    for sofier, balance in FINAL.items():
        
        info_sofier = data_sofiers.get(sofier, dict())
        bank_info = info_sofier.get('bank_checking_account', dict())
        
        list_final.append({
            'sofier': sofier,
            'nome': (info_sofier.get('full_name', None) or info_sofier.get('short_name', '')).strip(),
            'resgatado': balance.get('withdrawal', 0), 
            'análise': balance.get('VALIDATION', 0),
            'aprovado': balance.get('BLOCKED', 0),
            'disponível': balance.get('AVAILABLE', 0),
            'reprovado': balance.get('WRONG', 0),
            'cpf': info_sofier.get('document', ''),
            'modalidade': bank_info.get('account_type', ''),
            'banco': f"({bank_info.get('code', '')}) - {bank_info.get('name', '')}",
            'agência': bank_info.get('agency', ''),
            'conta': f"{bank_info.get('account', '')}-{bank_info.get('account_digit', '')}"
        })

    return fields, sorted(list_final, key=lambda x: x['nome'].upper())
    
    