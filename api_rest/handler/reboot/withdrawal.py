# coding: utf-8

from the_3rd.gmail.email_sender import EMailSender

from library.http.http_base import SofieHTTPHandler
from library.common.governance import LEVEL_APP_MYSOFIE


class Withdrawal(SofieHTTPHandler):
    """

    """
    def post(self):
        """

        :return:
        """
        email = EMailSender()
        email.subject = self.content_as_json.get('subject')
        email.to.extend(self.content_as_json.get('to'))
        email.msg = self.content_as_json.get('message')
        email()

        self.write_json({'SUCCESS': True})


HANDLERS = [
    ['withdrawal/?', Withdrawal, {'POST': [LEVEL_APP_MYSOFIE]}, 'withdrawal']
]