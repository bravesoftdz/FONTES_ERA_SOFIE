"""

"""

from csv import DictWriter

from library.storage.config import ConfigStorage
from micro_contract.transaction import Transaction

HEADERS = [
    'cupom',
    'nome',
    'email',
    'endereço',
    'bairro',
    'cidade',
    'uf',
    'cep',
    'ddd',
    'telefone',
    'cpf',
    'projeto',
    'sprom',
    'aprom',
    'vigência',
    'valor',
    'parcelas',
    'valor das parcelas'
]


def build_row(transaction: Transaction) -> dict:
    """

    :param transaction:
    :return:
    """
    return {
        'cupom': transaction.consumer.consumer,
        'nome': transaction.consumer.full_name.upper(),
        'email': transaction.consumer.email,
        'endereço': f'{transaction.address.type} {transaction.address.full_name}, {transaction.address.number} - {transaction.address.complement}',
        'bairro': transaction.address.district,
        'cidade': transaction.address.city,
        'uf': transaction.address.state,
        'cep': transaction.address.zipcode,
        'ddd': transaction.consumer.phone[0:2],
        'telefone': transaction.consumer.phone[2:],
        'cpf': transaction.consumer.consumer,
        'projeto': transaction.card.reference_codes[1],
        'sprom': '',
        'aprom': '',
        'vigência': transaction.card.reference_codes[2],
        'valor': transaction.payment_condition.price,
        'parcelas': transaction.payment_condition.quotes,
        'valor das parcelas': transaction.payment_condition.quote_value
    }


def main():
    """

    :return:
    """
    cursor = ConfigStorage().config['transaction'].find({'actors.company': 'abril', 'status.status': 'FINISHED', 'status.success': True}, {'transaction': 1})

    with open(r'c:\teste\abril.csv', 'w', newline='') as file_handler:
        file_writer = DictWriter(file_handler, fieldnames=HEADERS, delimiter=';', quotechar='"')
        file_writer.writeheader()

        for each in cursor:
            trans = Transaction(each['transaction'])
            row = build_row(trans)
            file_writer.writerow(row)


if __name__ == '__main__':
    main()
