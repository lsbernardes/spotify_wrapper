#!/usr/bin/env python
# coding: utf-8

import requests
from urllib.parse import urlencode
import base64
import datetime
import json
import os
from sys import exit
try:
    import webbrowser
    from colorama import Back, Fore, init, Style
except:
    print('Colorama e webbrowser não instalados')

class spotify:
#     COR1 = Back.WHITE + Fore.BLACK
    TOKEN = 'https://accounts.spotify.com/api/token'
    AUTH = 'https://accounts.spotify.com/authorize'
    REDIR = 'http://example.com/callback/'
    SCOPE = 'user-library-read user-read-private'
#     PATH = os.getenv('PYTHON_DEV')
    PATH = '/home/jovyan/spotify_wrapper'

    def __init__(self, ID=False, SECRET=False):
        self.BASIC = os.path.join(self.PATH, './json/basic_spotify.json')    
        self.CRED = os.path.join(self.PATH, './json/credential_spotify.json')
        self.NOW = datetime.datetime.now()
        self.CODE = None
        self.REFRESH = None
        self.ACCESS = None
        self.TMP = []
        self.ERROR = False

        if os.path.exists(self.BASIC) and os.path.getsize(self.BASIC) > 0:
            with open(self.BASIC, 'r') as f:
                self.BASIC_TMP = json.load(f)
            self.ID = self.BASIC_TMP['client_id']
            self.SECRET = self.BASIC_TMP['client_secret']

            if os.path.exists(self.CRED) and os.path.getsize(self.CRED) > 0:
                with open(self.CRED, 'r') as f:
                    self.STOR = json.load(f)
                    
                self.EXP = self.NOW > eval(self.STOR['expires'])
                self.ACCESS = self.STOR['access_token']
                self.CODE = self.STOR['code']
                if 'refresh_token' in self.STOR.keys():
                    self.REFRESH = self.STOR['refresh_token']
                    print('Refresh token existent!')

            else: 
                print('Obtendo Código de autorização...')
                self.EXP = False
                self.STOR = None
                self.auth()
        else:
            print('Não há credenciais básicas para usar a API do Spotify')
            exit()
            
    def auth(self):
        authQry = urlencode({ 'client_id': self.ID, 'response_type': 'code', 'redirect_uri': self.REDIR, 'scope': self.SCOPE })
        urlAuth = '{}?{}'.format(self.AUTH, authQry)
        print(urlAuth)
#         webbrowser.open(urlAuth)
        authCode = input('\n' + 'Pressione ENTER quando houver copiado a URL')
#         authCode = pyperclip.paste()
        self.CODE = authCode.partition('=')[2]
        print(self.CODE)
        self.getToken()

    def getToken(self, refresh=False):
        # constructing header
        base = bytes('{}:{}'.format(self.ID, self.SECRET), 'UTF-8')
        basecode = base64.b64encode(base)
        basecode = basecode.decode('UTF-8')
        head = 'Basic {}'.format(basecode)
        self.header = { 'Authorization': head }

        if not refresh or (not self.EXP or self.NOW > self.EXP):
            authQuery = { 'grant_type': 'authorization_code', 'code': self.CODE , 'redirect_uri': self.REDIR }
            self.token('Expired or not existent, getting a new Token...', authQuery)
        else:
            authQuery = { 'grant_type': 'refresh_token', 'refresh_token': self.REFRESH }
            self.token('Refreshing Token...', authQuery)

    def token(self, msg, authQuery):
            print('\n%s' % msg)
            url_token = requests.post(self.TOKEN, data=authQuery, headers=self.header)
            data = url_token.json()
            print(url_token.status_code)
            print(data)

            if url_token.status_code != 200:
                print('ERRO: status code {}'.format(url_token.status_code))
                if url_token.status_code == 400:
                    print('Authorization code expired, trying to obtain authorization code...')
                    self.auth()
            else:
                self.EXP = datetime.datetime.now() + datetime.timedelta(seconds=3600)
                data['expires'] = repr(self.EXP)
                data['code'] = self.CODE
                self.REFRESH = data['refresh_token']
                self.ACCESS = data['access_token']
                try:
                    with open(self.CRED, 'w') as f:
                        json.dump(data, f, indent=2)
                except:
                    print('Problemas gravando o arquivo JSON')

    def getLikedSongs(self, hide=False):
        ''' Baixar a playlista das minhas músicas salvas em SONGS '''
        self.TMP = []
        offset = 0
        cmd = 'https://api.spotify.com/v1/me/tracks'
        header = { 'Authorization': 'Bearer {}'.format(self.ACCESS) }
        query = urlencode({ 'limit': 50, 'offset': offset })
        url_token = requests.get(cmd, params=query, headers=header)
        
        command_data = url_token.json()
        print(json.dumps(command_data, indent=2, ensure_ascii=False))
        limite = command_data['total'] 
        if not hide:
            self.TMP.append(command_data)
        
        while offset < limite:
            offset += 50
            query = urlencode({ 'limit': 50, 'offset': offset })
            url_token = requests.get(cmd, params=query, headers=header)
            command_data = url_token.json()
            self.TMP.append(command_data)
            if 'error' in command_data.keys():
                self.ERROR = True
        
            if not hide:
                json.dumps(command_data, indent=2, ensure_ascii=False)

        if self.ERROR:
            print('Erro ao baixar informação. Função será executada de novo!')
            self.getLikedSongs()
        else:
            name_f = 'saved.json'
            with open(name_f, 'w') as f:
                json.dump(self.TMP, f, ensure_ascii=False)
            print('SAVED SONGS salvas')
