#!/usr/bin/env python
# coding: utf-8

import requests
from urllib.parse import urlencode
import base64
import datetime
import json
import os
import webbrowser
from sys import exit
from colorama import Back, Fore, init, Style

class spotify:
    COR1 = Back.WHITE + Fore.BLACK
    TOKEN = 'https://accounts.spotify.com/api/token'
    AUTH = 'https://accounts.spotify.com/authorize'
    REDIR = 'http://example.com/callback/'
    SCOPE = 'user-library-read user-read-private'
    PATH = os.getenv('PYTHON_DEV')

    def __init__(self, ID=False, SECRET=False):
        self.BASIC = os.path.join(PATH, './json/basic_spotify.json')    
        self.CRED = os.path.join(PATH, './json/credential_spotify.json')
        self.NOW = datetime.datetime.now()
        self.CODE = None
        self.REFRESH = None
        self.ACCESS = None
        self.TMP = []

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
        webbrowser.open(urlAuth)
        authCode = input('\n' + 'Pressione ENTER quando houver copiado a URL')
        authCode = pyperclip.paste()
        self.CODE = authCode.partition('=')[2]
        self.getToken()
    
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

    def getToken(self, refresh=False):
        if not refresh:
            authQuery = { 'grant_type': 'authorization_code', 'code': self.CODE , 'redirect_uri': self.REDIR }
        else:
            authQuery = { 'grant_type': 'refresh_token', 'refresh_token': self.REFRESH }

        # constructing header
        base = bytes('{}:{}'.format(self.ID, self.SECRET), 'UTF-8')
        basecode = base64.b64encode(base)
        basecode = basecode.decode('UTF-8')
        head = 'Basic {}'.format(basecode)
        self.header = { 'Authorization': head }
        
        if 'authorization_code' in authQuery['grant_type'] or (not self.EXP or self.NOW > self.EXP):
            self.token('Expired or not existent, getting a new Token...', authQuery)

        elif 'refresh_token' in authQuery['grant_type'] or (self.EXP and self.NOW < self.EXP):
            self.token('Refreshing Token...', authQuery)

    def getLikedSongs(self):
        ''' Baixar a playlista das minhas músicas salvas em SONGS '''
        self.TMP = []
        offset = 0
        cmd = 'https://api.spotify.com/v1/me/tracks'
        header = { 'Authorization': 'Bearer {}'.format(self.ACCESS) }
        query = urlencode({ 'limit': 50, 'offset': offset })
        url_token = requests.get(cmd, params=query, headers=header)
        
        command_data = url_token.json()
        print(json.dumps(command_data, indent=2))
        limite = command_data['total'] 
        self.TMP.append(command_data)
        
        while offset < limite:
            offset += 50
            query = urlencode({ 'limit': 50, 'offset': offset })
            url_token = requests.get(cmd, params=query, headers=header)
            command_data = url_token.json()
            self.TMP.append(command_data)

            json.dumps(command_data, indent=2)

        name_f = 'saved.json'
        with open(name_f, 'w') as f:
            json.dump(self.TMP, f)
        print('SAVED SONGS salvas')
