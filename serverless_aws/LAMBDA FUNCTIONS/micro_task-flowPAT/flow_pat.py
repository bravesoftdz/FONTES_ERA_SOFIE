from collections import namedtuple

Toggle = namedtuple('Toggle', ('index', 'statement', 'tip', 'context', 'required', 'options'))
Radio = namedtuple('Radio', ('index', 'statement', 'tip', 'context', 'required', 'options'))
Checkbox = namedtuple('Checkbox', ('index', 'statement', 'tip', 'context', 'required', 'options', 'next'))
Photo = namedtuple('Photo', ('index', 'statement', 'tip', 'context', 'required', 'min_qtt', 'max_qtt', 'next'))
Contact = namedtuple('Contact', ('index', 'statement', 'tip', 'context', 'required', 'fields', 'next'))
Message = namedtuple('Message', ('index', 'statement', 'tip', 'required', 'kind', 'next'))
Case = namedtuple('Case', ('index', 'variable', 'options'))
Integer = namedtuple('Integer', ('index', 'statement', 'tip', 'context', 'required', 'min_value', 'max_value', 'default_value', 'next'))
Finish = namedtuple('Finish', ('index', 'statement'))
Memo = namedtuple('Memo', ('index', 'statement', 'tip', 'context', 'required', 'next'))
SetVariable = namedtuple('SetVariable', ('index', 'next', 'variable', 'value'))

STYLE = {
    Toggle: 'toggle',
    Radio: 'radio', 
    Checkbox: 'checkbox',
    Photo: 'photo', 
    Contact: 'contact',
    Message: 'message',
    Memo: 'memo',
    Case: 'case',
    Integer: 'integer',
    Finish: 'finish',
    SetVariable: 'set_variable'
}

PRE_FLOW = [
    ################################################################################################
    Toggle(
        index=1,
        statement='Olá %sofier%, vamos vencer mais este desafio juntos!\n\nVocê está em **%sofie_place%?**',
        tip=None,
        context='LUGAR:CONFIRMACAO_VISUAL',
        required=True,
        options=[
            dict(label='SIM', value='SIM', next=8),
            dict(label='NÃO', value='NÃO', next=3)
        ]
    ),
    ################################################################################################
    Radio(
        index=3,
        statement='Puxa vida! Mas **O QUE VOCÊ ENCONTROU** neste local?',
        tip=None,
        context='LUGAR:ERRADO:CLASSIFICACAO',
        required=True,
        options=[
            dict(label='Um comércio com outro nome', value=None, next=5),
            dict(label='Um estabelecimento sem acesso livre', value=None, next=4),
            dict(label='Um comércio fechado pra sempre', value=None, next=4),
            dict(label='Uma residência ou condomínio', value=None, next=4),
            dict(label='Um terreno baldio', value=None, next=4),
            dict(label='Uma obra em andamento', value=None, next=4),
            dict(label='Não encontrei o número indicado', value=None, next=4)
        ]
    ),
    ################################################################################################
    Message(
        index=4,
        statement='%sofier%, esta informação é muito importante para nós.\n\nNos próximos passos pediremos algumas fotos e informações.\n\nSeja o mais detalhista possível e colete o máximo de evidências de que você não encontrou **%sofie_place%**.',
        tip=None,
        required=True,
        kind='success',
        next=20
    ),
    ################################################################################################
    Photo(
        index=20,
        statement='%sofier%, precisamos de uma **FOTO DA FACHADA** para os nossos registros.',
        tip=None,
        context='LUGAR:ERRADO:EVIDENCIA',
        min_qtt=1,
        max_qtt=6,
        required=True,
        next=21
    ),
    ################################################################################################
    Memo(
        index=21, 
        statement='Agora descreva, com o máximo de **DETALHES**, a situação.', 
        tip=None, 
        context='LUGAR:ERRADO:RELATO', 
        required=True, 
        next=9999
    ),
    ################################################################################################
    Toggle(
        index=5,
        statement='Interessante... E este comércio **É RELACIONADO À ALIMENTAÇÃO** como um restaurante ou mercado por exemplo?',
        tip=None,
        context='LUGAR:ERRADO:ALIMENTACAO',
        required=True,
        options=[
            dict(label='SIM', value='SIM', next=6),
            dict(label='NÃO', value='NÃO', next=4)
        ]
    ),
    ################################################################################################
    Radio(
        index=6,
        statement='Boa! Procure o responsável pelo estabelecimento, apresente-se, e verifique se **HÁ INTERESSE EM SE CREDENCIAR JUNTO À ALELO**.',
        tip=None,
        context='LUGAR:ERRADO:LEAD_ALELO',
        required=True,
        options=[
            dict(label='SIM', value='SIM', next=7),
            dict(label='NÃO', value='NÃO', next=4),
            dict(label='Já é credenciado Alelo', value='JAH_EH', next=4)
        ]
    ),
    ################################################################################################
    Contact(
        index=7,
        statement='Precisamos do **TELEFONE E EMAIL** deles.',
        tip=None,
        context='LUGAR:ERRADO:LEAD_ALELO:CONTATOS',
        required=True,
        fields=['phone', 'email'],
        next=4
    ),
    ################################################################################################
    Radio(
        index=8,
        statement='Show de bola! Nos diga:\n**ESTÁ FUNCIONANDO?**',
        tip=None,
        context='LUGAR:CERTO:PORTAS_ABERTAS',
        required=True,
        options=[
            dict(label='Sim, está funcionando', value=None, next=9300),
            dict(label='Está fora do horário de funcionamento', value=None, next=9),
            dict(label='Parece que fechou de vez', value=None, next=4),
        ]
    ),
    ################################################################################################
    Toggle(
        index=9,
        statement='Que pena %sofier%. Você gostaria de **VOLTAR DEPOIS** no horário de funcionamento ou prefere **CANCELAR A TAREFA?**',
        tip=None,
        context='SYSTEM:TASK:POSTPONE_OR_CANCEL',
        required=True,
        options=[
            dict(label='Retornarei amanhã', value='POSTPONE', next=11),
            dict(label='Cancelar o desafio', value='CANCEL', next=10)
        ]
    ),
    ################################################################################################
    Toggle(
        index=10,
        statement='Tá bom. Você **CONFIRMA O CANCELAMENTO** do desafio?',
        tip=None,
        context='SYSTEM:TASK:CANCEL',
        required=True,
        options=[
            dict(label='Sim, confirmo', value=True, next=8100),
            dict(label='Não, vou tentar de novo', value=False, next=8301)
        ]
    ),
    ################################################################################################
    SetVariable(
        index=8301,
        next=8,
        variable='SYSTEM:TASK:POSTPONE_OR_CANCEL',
        value='FINISH'
    ),    
    ################################################################################################
    Memo(
        index=8100, 
        statement='Por favor nos diga o **MOTIVO DA DESISTÊNCIA** para que possamos melhorar o aplicativo.', 
        tip=None, 
        context='SYSTEM:TASK:CANCEL:REASON', 
        required=True, 
        next=12
    ),
    ################################################################################################
    Message(
        index=11,
        statement='Bacana! Você tem mais **24 HORAS** para a realização deste desafio. Boa sorte!',
        tip=None,
        required=True,
        kind='success',
        next=9999
    ),
    ################################################################################################
    Message(
        index=12,
        statement='O desafio foi **CANCELADO** %sofier%.',
        tip=None,
        required=True,
        kind='failure',
        next=9999
    ),
    ################################################################################################
    # FIM DO PRÉ FLOW ##############################################################################
    ################################################################################################
]

FLOW = [
    ################################################################################################
    Toggle(
        index=9300,
        statement='Tem algum **ADESIVO ALELO** facilmente visível?',
        tip=None,
        context='ESTABELECIMENTO:ADESIVO',
        required=True,
        options=[
            dict(label='Sim', value=None, next=91),
            dict(label='Não', value=None, next=91),
        ]
    ),
    ################################################################################################
    Case(
        index=91,
        variable='produto',
        options=[
            dict(label='VR', value=45, next=92),
            dict(label='VA', value=46, next=93),
            dict(label='BOTH', value=47, next=94),
        ]
    ),
    ################################################################################################
    Radio(
        index=92,
        statement='Vamos lá então!\nQual é a **ATIVIDADE PRINCIPAL** deste lugar?',
        tip=None,
        context='ESTABELECIMENTO:ATIVIDADE',
        required=True,
        options=[
            dict(label='Restaurante', value=None, next=8300),
            dict(label='Fast food', value=None, next=8300),
            dict(label='Bar', value=None, next=8300),
            dict(label='Lanchonete', value=None, next=8300),
            dict(label='Padaria', value=None, next=8300),
            dict(label='Outros', value=None, next=8300)
        ]
    ),
    ################################################################################################
    Radio(
        index=93,
        statement='Vamos lá então!\nQual é a **ATIVIDADE PRINCIPAL** deste lugar?',
        tip=None,
        context='ESTABELECIMENTO:ATIVIDADE',
        required=True,
        options=[
            dict(label='Supermercado', value=None, next=8400),
            dict(label='Hipermercado', value=None, next=8400),
            dict(label='Mercearia', value=None, next=8400),
            dict(label='Armazém', value=None, next=8400),
            dict(label='Açougue', value=None, next=8500),
            dict(label='Peixaria', value=None, next=8500),
            dict(label='Hortimercado', value=None, next=8400),
            dict(label='Laticínios e frios', value=None, next=8500),
            dict(label='Outros', value=None, next=8500)
        ]
    ),
    ################################################################################################
    Radio(
        index=94,
        statement='Vamos lá então!\nQual é a **ATIVIDADE PRINCIPAL** deste lugar?',
        tip=None,
        context='ESTABELECIMENTO:ATIVIDADE',
        required=True,
        options=[
            dict(label='Restaurante', value=None, next=8300),
            dict(label='Fast food', value=None, next=8300),
            dict(label='Bar', value=None, next=8300),
            dict(label='Lanchonete', value=None, next=8300),
            dict(label='Padaria', value=None, next=8300),
            dict(label='Supermercado', value=None, next=8400),
            dict(label='Hipermercado', value=None, next=8400),
            dict(label='Mercearia', value=None, next=8400),
            dict(label='Armazém', value=None, next=8400),
            dict(label='Açougue', value=None, next=8500),
            dict(label='Peixaria', value=None, next=8500),
            dict(label='Hortimercado', value=None, next=8400),
            dict(label='Laticínios e frios', value=None, next=8500),
            dict(label='Outros', value=None, next=8500)
        ]
    ),
    ################################################################################################
    SetVariable(
        index=8300,
        next=8200,
        variable='ESTABELECIMENTO:TIPO',
        value='REFEICAO'
    ),
    ################################################################################################
    SetVariable(
        index=8400,
        next=8200,
        variable='ESTABELECIMENTO:TIPO',
        value='VAREJO'
    ),
    ################################################################################################
    SetVariable(
        index=8500,
        next=8200,
        variable='ESTABELECIMENTO:TIPO',
        value='CARNES_LATICINIOS'
    ),
    ################################################################################################
    Message(
        index=8200,
        statement='%sofier%, **NÃO É PERMITIDO** a compra e venda de Vale Refeição ou Alimentação.\nEntenda que vender ou comprar não é a mesma coisa de aceitar.',
        tip=None,
        required=True,
        kind='alert',
        next=95
    ),
    ################################################################################################
    Toggle(
        index=95,
        statement='Têm alguma **PLACA DE COMPRA E VENDA** de Vale Refeição ou Alimentação?',
        tip=None,
        context='ESTABELECIMENTO:COMPRA_TICKET',
        required=True,
        options=[
            dict(label='Sim', value=None, next=96),
            dict(label='Não', value=None, next=97)
        ]
    ),
    ################################################################################################
    Photo(
        index=96,
        statement='%sofier%, tire uma **FOTO DA PLACA** para os nossos registros por favor.',
        tip=None,
        context='ESTABELECIMENTO:COMPRA_TICKET:EVIDENCIA',
        min_qtt=1,
        max_qtt=2,
        required=True,
        next=97
    ),
    ################################################################################################
    Message(
        index=97,
        statement='Agora é uma boa hora para **SE APRESENTAR** ao responsável pelo estabelecimento informando que você esta realizando uma pesquisa para a Alelo Refeições.',
        tip=None,
        required=True,
        kind='instruction',
        next=8000
    ),
    ################################################################################################
    Radio(
        index=8000,
        statement='A pessoa com quem você está falando **ACEITA RESPONDER** algumas perguntas?',
        tip=None,
        context='ESTABELECIMENTO:ENGAJAMENTO',
        required=True,
        options=[
            dict(label='Sim', value=None, next=98),
            dict(label='Não', value=None, next=9),
            dict(label='Não é mais credenciado Alelo', value=None, next=20)
        ]
    ),
    ################################################################################################
    Radio(
        index=98,
        statement='Qual é o **TAMANHO DA ÁREA** do estabelecimento? Mais ou menos, não precisa ser exato.',
        tip='A área é a multiplicação da largura pela profundidade. Exemplo 5 vezes 5 é igual à 25. Essa seria a área do restaurante.',
        context='ESTABELECIMENTO:AREA',
        required=True,
        options=[
            dict(label='Até 10 m²', value=None, next=9100),
            dict(label='Até 50 m²', value=None, next=9100),
            dict(label='Até 100 m²', value=None, next=9100),
            dict(label='Até 150 m²', value=None, next=9100),
            dict(label='Até 200 m²', value=None, next=9100),
            dict(label='Até 300 m²', value=None, next=9100),
            dict(label='Até 500 m²', value=None, next=9100),
            dict(label='Acima de 1.000 m²', value=None, next=9100),
        ]
    ),
    ################################################################################################
    Case(
        index=9100,
        variable='ESTABELECIMENTO:TIPO',
        options=[
            dict(label='REFEICAO', value='REFEICAO', next=910),
            dict(label='VAREJO', value='VAREJO', next=99),
            dict(label='CARNES_LATICINIOS', value='CARNES_LATICINIOS', next=99)
        ]
    ),
    ################################################################################################
    Integer(
        index=99,
        statement='Quantos **CAIXAS DE PAGAMENTO** existe no estabelecimento?',
        tip=None,
        context='ESTABELECIMENTO:CAIXAS',
        required=True,
        min_value=0,
        max_value=0,
        default_value=0,
        next=910
    ),
    ################################################################################################
    Checkbox(
        index=910,
        statement='Tudo bacana até aqui. Agora nos diga:\nQuais são os **DIAS DA SEMANA** de funcionamento?',
        tip=None,
        context='ESTABELECIMENTO:EXPEDIENTE:DIAS',
        required=True,
        options=[
            dict(label='Dias úteis (segunda à sexta)', value=None),
            dict(label='Aos sábados', value=None),
            dict(label='Aos domingos', value=None),
        ],
        next=911
    ),
    ################################################################################################
    Checkbox(
        index=911,
        statement='E os **HORÁRIOS** de funcionamento?',
        tip=None,
        context='ESTABELECIMENTO:EXPEDIENTE:HORARIO',
        required=True,
        options=[
            dict(label='Funciona de dia', value='DIA'),
            dict(label='Funciona de noite', value='NOITE'),
            dict(label='Funciona 24 horas por dia', value='24H'),
        ],
        next=912
    ),
    ################################################################################################
    Toggle(
        index=912,
        statement='E **ACEITA RECEBER ADESIVOS** de sinalização Alelo?',
        tip=None,
        context='ESTABELECIMENTO:ACEITA:ADESIVO',
        required=True,
        options=[
            dict(label='Sim', value=None, next=9101),
            dict(label='Não', value=None, next=9101)
        ]
    ),
    ################################################################################################
    Case(
        index=9101,
        variable='ESTABELECIMENTO:TIPO',
        options=[
            dict(label='REFEICAO', value='REFEICAO', next=914),
            dict(label='VAREJO', value='VAREJO', next=940),
            dict(label='CARNES_LATICINIOS', value='CARNES_LATICINIOS', next=9103)
        ]
    ),
    ################################################################################################
    Integer(
        index=914,
        statement='Qual é a quantidade de **MESAS** do restaurante?',
        tip=None,
        context='ESTABELECIMENTO:EQUIPAMENTO:MESA',
        required=True,
        min_value=0,
        max_value=0,
        default_value=0,
        next=915
    ),
    ################################################################################################
    Integer(
        index=915,
        statement='E qual é a quantidade **TOTAL DE ASSENTOS** do restaurante?',
        tip=None,
        context='ESTABELECIMENTO:EQUIPAMENTO:ASSENTOS',
        required=True,
        min_value=0,
        max_value=0,
        default_value=0,
        next=941
    ),
    ################################################################################################
    Toggle( #: <====== AQUI
        index=940,
        statement='Vende **ALIMENTOS SAUDÁVEIS** como FRUTAS, SUCOS, VITAMINAS ou SALADAS?',
        tip=None,
        context='ESTABELECIMENTO:OFERTA:ALIMENTOS_SAUDAVEIS',
        required=True,
        options=[
            dict(label='Sim', value=True, next=9103),
            dict(label='Não', value=False, next=9103)
        ]
    ),
    ################################################################################################
    Case(
        index=9103,
        variable='ESTABELECIMENTO:TIPO',
        options=[
            dict(label='REFEICAO', value='REFEICAO', next=941),
            dict(label='VAREJO', value='VAREJO', next=920),
            dict(label='CARNES_LATICINIOS', value='CARNES_LATICINIOS', next=920)
        ]
    ),
    ################################################################################################
    Toggle( #: <====== AQUI
        index=941,
        statement='E este estabelecimento possui algum **CARDÁPIO, PAINEL ou LETREIRO** indicando FRUTAS, SUCOS, VITAMINAS ou SALADAS?',
        tip=None,
        context='ESTABELECIMENTO:OFERTA:OPCOES_VISIVEIS',
        required=True,
        options=[
            dict(label='Sim', value=True, next=920),
            dict(label='Não', value=False, next=920)
        ]
    ),
    ################################################################################################
    Contact(
        index=920,
        statement='Qual é o melhor **TELEFONE E EMAIL** do responsável pelo estabelecimento? Estas informações são importantes para a Alelo.',
        tip=None,
        context='ESTABELECIMENTO:CONTATOS',
        required=True,
        fields=['phone', 'email'],
        next=951
    ),
    ################################################################################################
    Radio(
        index=951,
        statement='Sobre Antecipação de Recebíveis:\n**SABE O QUE É?**',
        tip=None,
        context='ESTABELECIMENTO:ANTECIPACAO:CONHECE',
        required=True,
        options=[
            dict(label='Sim, sabe com certeza', value=None, next=952),
            dict(label='Meio que já ouviu falar', value=None, next=952),
            dict(label='Não sabe do que se trata', value=None, next=952),
        ]
    ),
    ################################################################################################
    Radio(
        index=952,
        statement='E **RECEBE ALGUM TIPO** de Antecipação de Recebíveis?',
        tip=None,
        context='ESTABELECIMENTO:ANTECIPACAO:RECEBE',
        required=True,
        options=[
            dict(label='A pessoa não soube informar', value=None, next=953),
            dict(label='Não, eles não recebem antecipação de recebíveis', value=None, next=953),
            dict(label='Sim e eles recebem pelo BANCO', value=None, next=930),
            dict(label='Sim e eles recebem pela OPERADORA DA MAQUININHA', value=None, next=930),
            dict(label='Sim e eles recebem pela OPERADORA DO VALE REFEIÇÃO OU ALIMENTAÇÃO', value=None, next=930)
        ]
    ),
    ################################################################################################
    Toggle(
        index=953,
        statement='E gostaria de **MAIS INFORMAÇÕES** sobre Antecipação de Recebíveis?',
        tip=None,
        context='ESTABELECIMENTO:ANTECIPACAO:ACEITA_INFO',
        required=True,
        options=[
            dict(label='Sim', value=None, next=930),
            dict(label='Não', value=None, next=930)
        ]
    ),
    ################################################################################################
    Integer(
        index=930,
        statement='Ufa, estamos terminando! Quantos **FUNCIONÁRIOS** trabalham neste estabelecimento?',
        tip=None,
        context='ESTABELECIMENTO:FUNCIONARIOS',
        required=True,
        min_value=0,
        max_value=0,
        default_value=0,
        next=9201
    ),
]    

PHOTOS = [
    ################################################################################################
    Case(
        index=9201,
        variable='ESTABELECIMENTO:TIPO',
        options=[
            dict(label='REFEICAO', value='REFEICAO', next=9206),
            dict(label='VAREJO', value='VAREJO', next=9203),
            dict(label='CARNES_LATICINIOS', value='CARNES_LATICINIOS', next=9200)
        ]
    ),
    ################################################################################################
    Photo(
        index=9203,
        statement='Uma foto dos **ALIMENTOS SAUDÁVEIS**.',
        tip=None,
        context='ESTABELECIMENTO:FOTO:ALIMENTOS_SAUDAVEIS',
        required=True,
        min_qtt=1,
        max_qtt=2,
        next=9200
    ),
    ################################################################################################
    Case(
        index=9206,
        variable='ESTABELECIMENTO:OFERTA:OPCOES_VISIVEIS',
        options=[
            dict(label='Sim', value=True, next=9406),
            dict(label='Não', value=False, next=9200),
        ]
    ),
    ################################################################################################
    Photo(
        index=9406,
        statement='Tire uma foto do **CARDÁPIO, PAINEL ou LETREIRO** na parte de FRUTAS, SUCOS, VITAMINAS ou SALADAS.',
        tip=None,
        context='ESTABELECIMENTO:FOTO:CARDAPIO',
        required=True,
        min_qtt=1,
        max_qtt=2,
        next=9200
    ),
    ################################################################################################
    Photo(
        index=9200, # 9202
        statement='Agora uma **FOTO DO INTERIOR** do estabelecimento.',
        tip=None,
        context='ESTABELECIMENTO:FOTO:INTERIOR',
        required=True,
        min_qtt=1,
        max_qtt=2,
        next=9250 # 9203
    ),
    ################################################################################################
    Photo(
        index=9250, # 9200
        statement='Tire uma foto caprichada da **FACHADA FRONTAL** do estabelecimento.',
        tip=None,
        context='ESTABELECIMENTO:FOTO:FACHADA',
        required=True,
        min_qtt=1,
        max_qtt=2,
        next=9600
    ),
    ################################################################################################
    Memo(
        index=9600, 
        statement='Por fim, o responsável pelo estabelecimento deseja enviar uma **MENSAGEM À ALELO**?', 
        tip=None, 
        context='ESTABELECIMENTO:MENSAGEM', 
        required=False, 
        next=9999
    )
]

POS_FLOW = [
    ################################################################################################
    Finish(
        index=9999,
        statement='Agradecemos pelo seu empenho. Aproveite este momento para **COMENTAR** como foi a sua experiência.'
    ),
]

ALL_FLOW = PRE_FLOW + FLOW + PHOTOS + POS_FLOW
FINAL_LIST = list()

for each in ALL_FLOW:
    style = STYLE.get(each.__class__, None)
    if not style:
        raise Exception(f'Estilo não reconhecido: {each.__class__.__name__}')
    
    item = dict()
    item['style'] = style
    
    for prop in each._fields:
        item[prop] = getattr(each, prop)
    
    FINAL_LIST.append(item)
    

def generate_flow():
    """
    
    """
    import boto3
    
    boto3.resource('dynamodb').Table('table_micro_task_flows').put_item(
        Item={
            'name': 'PAT', 
            'version': 1, 
            'task_flow': FINAL_LIST
        }
    )
    
    return sorted([each['index'] for each in FINAL_LIST])
