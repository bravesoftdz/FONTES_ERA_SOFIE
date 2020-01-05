# coding: utf-8

"""

"""

from csv import DictWriter
from tempfile import SpooledTemporaryFile

from crud.sofier import SofierCRUD
from library.common.governance import DEVELOPER_SESSION
from library.common.miscellaneous import phone_mask
from library.common.paging_info import PagingInfo
from the_3rd.gmail.email_sender import EMailSender


class SofierPerformance(object):
    """

    """

    FIELDS = [
        'CADASTRO',
        'NOME',
        'TRATAMENTO',
        'NASCIMENTO',
        'TELEFONE',
        'EMAIL',
    ]

    def __call__(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        file_handler = SpooledTemporaryFile(mode='w+t', encoding='UTF-8')
        file_handler.write(u'\ufeff')
        file_writer = DictWriter(file_handler, fieldnames=SofierPerformance.FIELDS, delimiter=';', quotechar='"')
        file_writer.writeheader()

        try:
            list_sofier = SofierCRUD(PagingInfo(), DEVELOPER_SESSION).listing()['data']

            record_base = {key: None for key in SofierPerformance.FIELDS}

            for sofier in list_sofier:
                record = record_base.copy()

                record['CADASTRO'] = sofier['__created__']['when'].strftime('%d/%m/%Y %H:%M')
                record['NOME'] = sofier.get('full_name', '')
                record['TRATAMENTO'] = sofier['short_name']
                record['NASCIMENTO'] = sofier['birthday'].strftime('%d/%m/%Y')
                record['TELEFONE'] = phone_mask(sofier.get('main_phone', ''))
                record['EMAIL'] = sofier['email']

                file_writer.writerow(record)

            file_handler.seek(0)

            email = EMailSender()
            email.to.append('mario.guedes@mysofie.com')
            email.subject = 'Relação de Sofiers'
            email.attachments['report.csv'] = ('text/csv', file_handler.read())
            email()
        finally:
            file_handler.close()


if __name__ == '__main__':
    report = SofierPerformance()
    report()
