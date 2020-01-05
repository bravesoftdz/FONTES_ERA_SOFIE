"""
Your module description
"""


def get_reports():
    """
    
    """
    SOFIERS = {
        'name': 'SOFIERS',
        'label': 'Listagem de sofiers',
        'params': [
            {'query_string': 'start_when', 'format': 'DATE', 'label': 'Início'},
            {'query_string': 'finish_when', 'format': 'DATE', 'label': 'Fim'}
        ],
        'actions': [
            {'label': 'CSV', 'value': 'CSV'}
        ]
    }
    
    SALDOS = {
        'name': 'SALDOS',
        'label': 'Saldos monetários dos sofiers',
        'params': [],
        'actions': [
            {'label': 'CSV', 'value': 'CSV'}
        ]
    }
    
    EXTRATO = {
        'name': 'EXTRATO',
        'label': 'Extrato de movimentação financeira',
        'params': [
            {'query_string': 'sofier', 'format': 'SOFIER', 'label': 'Sofier'}
        ],
        'actions': [
            {'label': 'CSV', 'value': 'CSV'}
        ]
    }
    
    RESERVADOS = {
        'name': 'RESERVADOS',
        'label': 'Lista de desafios reservados',
        'params': [],
        'actions': [
            {'label': 'CSV': 'value': 'CSV'}
        ]
    }
    
    return {
        'data': [SOFIERS, SALDOS, EXTRATO, RESERVADOS] 
    }