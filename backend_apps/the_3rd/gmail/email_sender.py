# coding: utf-8

"""

"""

from base64 import urlsafe_b64encode
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from httplib2 import Http
from os import path

from apiclient.discovery import build
from oauth2client import file as oauth_file, client, tools

SCOPES = 'https://www.googleapis.com/auth/gmail.compose'


class EMailSender(object):
    """
    Inspirado em: https://stackoverflow.com/questions/920910/sending-multipart-html-emails-which-contain-embedded-images
    """

    def __init__(self):
        """
        Inicializa o obejto
        """
        self.to = list()
        self.subject = ''
        self.msg = ''
        self.cc = list()
        self.cco = list()
        self.attachments = dict()

    def __call__(self):
        """

        :return:
        """
        try:
            token_file = path.join(path.dirname(path.realpath(__file__)), 'token.json')
            store = oauth_file.Storage(token_file)
            creds = store.get()
            if not creds or creds.invalid:
                credentials_file = path.join(path.dirname(path.realpath(__file__)), 'credentials.json')
                flow = client.flow_from_clientsecrets(credentials_file, SCOPES)
                tools.run_flow(flow, store)

            service = build('gmail', 'v1', http=creds.authorize(Http()))

            message = MIMEMultipart(_subtype='related')
            message.preamble = 'Mensagem da Plataforma Sofie Tecnologia LTDA'
            message['subject'] = self.subject
            message['from'] = '"Assistente Sofie" <sofie@mysofie.com>'
            message['to'] = ', '.join(self.to)
            if self.cc:
                message['cc'] = ', '.join(self.cc)
            if self.cco:
                message['cco'] = ', '.join(self.cco)

            message.attach(MIMEText(self.msg, _subtype='html'))

            if self.attachments:
                for key, value in self.attachments.items():
                    if isinstance(value, tuple):
                        mime, content = value
                        discreet = mime.split('/')[0]

                        if discreet == 'text':
                            part = MIMEText(content)

                        else:
                            raise Exception('MIME TYPE não suportado pelo EMailSender')

                        part.add_header('Content-ID', '<{}>'.format(key))
                        message.attach(part)

                    else:
                        image = MIMEImage(value)
                        image.add_header('Content-ID', '<{}>'.format(key))
                        message.attach(image)

            content = {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

            sended = service.users().messages().send(userId='me', body=content).execute()

            return sended
        except Exception as err:
            pass


if __name__ == '__main__':
    email = EMailSender()

    email.to.extend(['mario.guedes@mysofie.com', 'jmarioguedes@gmail.com'])
    email.subject = 'EMAIL DE TESTE'
    email.msg = '<img src="cid:cover"><br/><strong>Veio um mapa?.</strong><br>'

    from the_3rd.google_maps.static import return_static_map

    email.attachments['cover'] = return_static_map("-23.5021638", "-46.850293")

    email()
