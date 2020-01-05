import json


DATA = {
    'data': [
        {'code': '001', 'name': 'Banco do Brasil'},  #: OK
        {'code': '003', 'name': 'Banco da Amazônia'},  #: OK
        {'code': '004', 'name': 'Banco do Nordeste do Brasil'},
        {'code': '104', 'name': 'Caixa Econômica Federal'},  #: OK
        # {'code': '070', 'name': 'Banco de Brasília'},
        # {'code': '047', 'name': 'Banco do Estado de Sergipe'},
        # {'code': '021', 'name': 'Banco do Estado do Espírito Santo'},
        # {'code': '037', 'name': 'Banco do Estado do Pará'},
        # {'code': '041', 'name': 'Banco do Estado do Rio Grande do Sul'},
        # {'code': '075', 'name': 'Banco ABN Amro S.A.'},
        # {'code': '025', 'name': 'Banco Alfa'},
        # {'code': '719', 'name': 'Banco Banif'},
        # {'code': '107', 'name': 'Banco BBM'},
        # {'code': '318', 'name': 'Banco BMG'},
        # {'code': '218', 'name': 'Banco Bonsucesso'},
        # {'code': '208', 'name': 'Banco BTG Pactual'},
        # {'code': '263', 'name': 'Banco Cacique'},
        # {'code': '473', 'name': 'Banco Caixa Geral - Brasil'},
        {'code': '745', 'name': 'Banco Citibank'},  #: OK
        # {'code': '721', 'name': 'Banco Credibel'},
        # {'code': '505', 'name': 'Banco Credit Suisse'},
        # {'code': '265', 'name': 'Banco Fator'},
        # {'code': '224', 'name': 'Banco Fibra'},
        {'code': '121', 'name': 'Agibank'},  #: OK
        # {'code': '612', 'name': 'Banco Guanabara'},
        # {'code': '604', 'name': 'Banco Industrial do Brasil'},
        # {'code': '320', 'name': 'Banco Industrial e Comercial'},
        # {'code': '653', 'name': 'Banco Indusval'},
        {'code': '077', 'name': 'Banco Inter'},  #: OK
        # {'code': '184', 'name': 'Banco Itaú BBA'},
        # {'code': '479', 'name': 'Banco ItaúBank'},
        # {'code': '389', 'name': 'Banco Mercantil do Brasil'},
        # {'code': '746', 'name': 'Banco Modal'},
        # {'code': '738', 'name': 'Banco Morada'},
        # {'code': '623', 'name': 'Banco Pan'},
        # {'code': '611', 'name': 'Banco Paulista'},
        # {'code': '643', 'name': 'Banco Pine'},
        # {'code': '654', 'name': 'Banco Renner'},
        # {'code': '741', 'name': 'Banco Ribeirão Preto'},
        {'code': '422', 'name': 'Banco Safra'},
        {'code': '033', 'name': 'Banco Santander'},  #: OK
        # {'code': '637', 'name': 'Banco Sofisa'},
        {'code': '237', 'name': 'Bradesco'},  #: OK
        {'code': '341', 'name': 'Itaú Unibanco'},  #: OK
        {'code': '212', 'name': 'Banco Original'},  #: OK
        {'code': '260', 'name': 'Nu Pagamentos S.A'},  #: OK
    ]
}


def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps(DATA)
    }
