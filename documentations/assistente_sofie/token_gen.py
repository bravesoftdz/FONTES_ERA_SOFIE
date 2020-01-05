# coding: utf-8

"""

"""

from oauth2client import file as oauth_file, client, tools

SCOPES = 'https://www.googleapis.com/auth/gmail.compose'

store = oauth_file.Storage('token.json')
flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
tools.run_flow(flow, store)
