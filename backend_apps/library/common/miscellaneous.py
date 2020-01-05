# coding: utf-8

"""
Aglutina diversas constantes, rotinas de validação, higienização e por ai vai
"""

from datetime import datetime
from re import compile
from unicodedata import normalize, combining
from json import dumps

from library.common.debug_mode import IN_DEBUG_MODE

REGEX_MAIL = r'''(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'''

REGEX_ISODATE = compile(r'\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}[+-]\d{4})?')


def json_serial(obj):
    """
    Função com o objetivo de transformar um objeto Python em um JSON

    Foi criado para suportar o tipo datetime sem o incoveniente do par `$date`

    Deve ser utilizado em conjunto com `json.dumps`

    :param obj:
        Fragmento de informação
    :return:
        Saída no formato adequado em JSON
    """
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S.%f')
    else:
        return obj


def to_json(content: dict) -> str:
    """
    Serializa um tipo Python em string JSON

    :param content:
        Conteudo a ser serializado em JSON
    :return:
        JSON
    """
    return dumps(content, default=json_serial, sort_keys=IN_DEBUG_MODE, indent=4 if IN_DEBUG_MODE else None)


def object_deserialize(obj):
    """
    Função com o objetivo de intrepretar os valores de um JSON, transformando para tipos Python

    Foi criado para suportar o tipo datetime sem o incoveniente do par `$date`

    **Méritos ao Thiago Filadelfo pela sugestão**

    :param obj:
        Dicionário com a interpretação rasa do JSON
    :return:
        Objeto Python equivalente ao JSON
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str):
                if REGEX_ISODATE.match(obj[key]):
                    date_len = len(obj[key])

                    if date_len == 10:
                        obj[key] = datetime.strptime(value, '%Y-%m-%d')
                    elif date_len == 19:
                        if 'T' in value:
                            obj[key] = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
                        else:
                            obj[key] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    elif date_len == 26:
                        obj[key] = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
                    else:
                        obj[key] = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
            elif isinstance(value, dict):
                object_deserialize(value)
            elif isinstance(value, list):
                for each in value:
                    if isinstance(each, dict):
                        object_deserialize(each)

    return obj


def cpf_is_valid(cpf: str) -> bool:
    """
    Valida o CPF de acordo com o algoritmo descrito em:

    https://dicasdeprogramacao.com.br/algoritmo-para-validar-cpf/

    :param cpf:
        CPF a ser validado
    :return:
        Indicação se o CPF é válido, `True`, ou inválido, `False`
    """
    assert isinstance(cpf, str), 'Tipo inválido'

    numbers = [int(digit) for digit in cpf if digit.isdigit()]

    if len(numbers) != 11:
        return False

    if len([each for each in numbers[1:] if each != numbers[0]]) == 0:
        return False

    factors = [i for i in range(10, 1, -1)]
    digit_1 = sum([digit * factors[idx] for idx, digit in enumerate(numbers[0:9])]) * 10 % 11
    if digit_1 > 9:
        digit_1 = 0

    factors = [i for i in range(11, 1, -1)]
    digit_2 = sum([digit * factors[idx] for idx, digit in enumerate(numbers[0:10])]) * 10 % 11
    if digit_2 > 9:
        digit_2 = 0

    return numbers[9] == digit_1 and numbers[10] == digit_2


def cnpj_is_valid(cnpj: str) -> bool:
    """
    Valida o CNPJ de acordo com o algoritmo descrito em:

    http://www.macoratti.net/alg_cnpj.htm

    :param cnpj:
        CNPJ a ser validado
    :return:
        Indicação se o CNPJ é válido, `True`, ou inválido, `False`
    """
    assert isinstance(cnpj, str), 'Tipo inválido'

    numbers = [int(digit) for digit in cnpj if digit.isdigit()]

    if len(numbers) != 14:
        return False

    factors = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digit_1 = sum([digit * factors[idx] for idx, digit in enumerate(numbers[0:12])]) % 11
    if digit_1 < 2:
        digit_1 = 0
    else:
        digit_1 = 11 - digit_1

    factors = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digit_2 = sum([digit * factors[idx] for idx, digit in enumerate(numbers[0:13])]) % 11
    if digit_2 < 2:
        digit_2 = 0
    else:
        digit_2 = 11 - digit_2

    return numbers[12] == digit_1 and numbers[13] == digit_2


def datetime2string(date_time: datetime, format_: str = '%Y-%m-%dT%H:%M:%S') -> str:
    """
    Converte datetime em string

    :param date_time:
        Objeto datetime
    :param format_:
        Formato desejado
    :return:
    """

    return date_time.strftime(format_)


def sanitize_text(original_text: str) -> str:
    """
    Retira caracteres diacríticos

    >>> sanitize_text('Coração')
    'coracao'

    :param original_text:
        Texto original a ser analizado
    :return:
        Resultado sem diacríticos
    """
    if not isinstance(original_text, str):
        return original_text

    normal = normalize('NFD', original_text)
    shaved = ''.join(c for c in normal if not combining(c))
    final = normalize('NFC', shaved)

    return final.lower() if final else ''


def anonymize_email(email: str) -> str:
    """

    :param email:
    :return:
    """
    user, server = email.split('@')
    user = user.replace(user[1:-1], '*' * len(user[1:-1]))

    return ''.join([user, '@', server])


def phone_mask(number: str or None) -> str:
    """
    Aplica a máscara de telefone a uma string

    :param number:
        String a ser formatada
    :return:
        String formatada
    """
    if not number:
        return ''
    else:
        tam = len(number)

        if tam == 8:
            return '{}-{}'.format(number[:4], number[4:])
        elif tam == 10:
            return '({}) {}-{}'.format(number[:2], number[2:6], number[6:])
        elif tam == 9:
            return '{}-{}-{}'.format(number[:1], number[1:5], number[5:])
        elif tam == 11:
            return '({}) {}-{}-{}'.format(number[:2], number[2], number[3:7], number[7:])
        else:
            return number


if __name__ == '__main__':
    print('# Higienização de texto')
    print(sanitize_text('coração'))
    print(sanitize_text('mario.guedes'))

    print('# Validação de CPFs')
    print(cpf_is_valid('196.783.358-32'))
    print(cpf_is_valid('199.789.359-32'))
    print(cpf_is_valid('111.111.111-11'))
    print('\n')
    print('# Testando com CNPJs')
    print(cnpj_is_valid('11.222.333/0001-81'))
    print(cnpj_is_valid('56324114000141'))
