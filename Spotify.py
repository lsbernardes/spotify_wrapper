#!/usr/bin/env python
# coding: utf-8

LANGUAGE = { 
            'eng': 
                { 
                1: '"webbrowser" not installed', 
                2: 'Obtaining Authorization code...',
                3: 'There is no basic credentials to use Spotify API',
                4: 'Refresh token existent!',
                5: 'When the URL has been copied to the clipboard press ENTER key',
                6: 'Token expired or not existent, getting a new Token...',
                7: 'Refreshing Token...',
                8: 'ERROR: status code {}',
                9: 'Authorization code expired, trying to obtain a new authorization code...',
                10: 'Problem generating the JSON file',
                11: 'LIKED SONGS stored'
                }
            'pt-br':
                { 
                1: '"webbrowser" não instalado', 
                2: 'Obtendo Código de autorização...',
                3: 'Não há credenciais básicas para usar a API do Spotify',
                4: 'Parêmtro "Refresh token" existe',
                5: 'Pressione ENTER quando houver copiado a URL',
                6: 'Token expirado ou não existente, obtendo um novo Token...',
                7: 'Atualizando Token...',
                8: 'ERRO: código {}',
                9: 'Código de autorização expirado, tentando obter um novo código de autorização...',
                10: 'Problemas gravando o arquivo JSON',
                11: 'LIKED SONGS gravado'
                }
            
            }

set_LANG = 'eng'

import requests
from urllib.parse import urlencode, urlparse
import base64
import datetime
import json
import os
from sys import exit
try:
    import webbrowser
except:
    print(LANGUAGE[set_LANG][1])

class spotify:
    TOKEN = 'https://accounts.spotify.com/api/token'
    AUTH = 'https://accounts.spotify.com/authorize'
    REDIR = 'http://example.com/callback/'
    SCOPE = 'user-library-read user-read-private'
    PATH = os.getenv('PYTHON_DEV')

    def __init__(self, ID=False, SECRET=False):
        self.BASIC = os.path.join(self.PATH, './json/basic_spotify.json')    
        self.CRED = os.path.join(self.PATH, './json/credential_spotify.json')
        self.NOW = datetime.datetime.now()
        self.CODE = None
        self.REFRESH = None
        self.ACCESS = None
        self.TMP = []
        self.ERROR = False

        if ID and SECRET:
            self.ID = ID
            self.SECRET = SECRET
            self.check_credentials()

        elif os.path.exists(self.BASIC) and os.path.getsize(self.BASIC) > 0:
            with open(self.BASIC, 'r') as f:
                self.BASIC_TMP = json.load(f)
            self.ID = self.BASIC_TMP['client_id']
            self.SECRET = self.BASIC_TMP['client_secret']
            self.check_credentials()

            else: 
                print(LANGUAGE[set_LANG][2])
                self.EXP = False
                self.STOR = None
                self.auth()
        else:
            print(LANGUAGE[set_LANG][3])
            exit()
    
    def check_credentials(self):
        if os.path.exists(self.CRED) and os.path.getsize(self.CRED) > 0:
            with open(self.CRED, 'r') as f:
                self.STOR = json.load(f)
                
            self.EXP = self.NOW > eval(self.STOR['expires'])
            self.ACCESS = self.STOR['access_token']
            self.CODE = self.STOR['code']
            if 'refresh_token' in self.STOR.keys():
                self.REFRESH = self.STOR['refresh_token']
                print(LANGUAGE[set_LANG][4])

    def auth(self):
        authQry = urlencode({ 'client_id': self.ID, 'response_type': 'code', 'redirect_uri': self.REDIR, 'scope': self.SCOPE })
        urlAuth = '{}?{}'.format(self.AUTH, authQry)
        print(urlAuth)
        webbrowser.open(urlAuth)
        input('\n' + LANGUAGE[set_LANG][5])
        authCode = pyperclip.paste()
        self.CODE = urlparse(authCode).query
        self.CODE = self.CODE.partition('=')[-1]
        self.getToken()

    def getToken(self, refresh=False):
        # constructing header
        base = bytes('{}:{}'.format(self.ID, self.SECRET), 'UTF-8')
        basecode = base64.b64encode(base)
        basecode = basecode.decode('UTF-8')
        head = 'Basic {}'.format(basecode)
        self.header = { 'Authorization': head }

        if not refresh or not self.EXP:
            authQuery = { 'grant_type': 'authorization_code', 'code': self.CODE , 'redirect_uri': self.REDIR }
            self.token(LANGUAGE[set_LANG][6], authQuery)
        else:
            authQuery = { 'grant_type': 'refresh_token', 'refresh_token': self.REFRESH }
            self.token(LANGUAGE[set_LANG][7], authQuery)

    def token(self, msg, authQuery):
            print('\n%s' % msg)
            url_token = requests.post(self.TOKEN, data=authQuery, headers=self.header)
            data = url_token.json()
            print(url_token.status_code)
            print(data)

            if url_token.status_code != 200:
                print(LANGUAGE[set_LANG][8].format(url_token.status_code))
                if url_token.status_code == 400:
                    print(LANGUAGE[set_LANG][9])
                    self.auth()
            else:
                try:
                    self.REFRESH = data['refresh_token']
                except:
                    pass
                self.EXP = datetime.datetime.now() + datetime.timedelta(seconds=3600)
                self.ACCESS = data['access_token']
                data['expires'] = repr(self.EXP)
                data['code'] = self.CODE
                try:
                    with open(self.CRED, 'w') as f:
                        json.dump(data, f, indent=2)
                except:
                    print(LANGUAGE[set_LANG][10])

    def testExpired(self, json):
        if 'error' in json.keys():
            print(json['error'])
            if json['error']['status'] == 401:
                self.getToken(True)
                return True
        else:
            return False
    
    def getLikedSongs(self, hide=False):
        ''' Baixar a playlista das minhas músicas salvas em SONGS '''

        self.TMP = []
        cmd = 'https://api.spotify.com/v1/me/tracks'
        header = { 'Authorization': 'Bearer {}'.format(self.ACCESS) }
        query = urlencode({ 'limit': 50, 'offset': 0 })
        
        url_token = requests.get(cmd, params=query, headers=header)
        command_data = url_token.json()
        if self.testExpired(command_data):
            url_token = requests.get(cmd, params=query, headers=header)
            command_data = url_token.json()
            
        if not hide:
            print(json.dumps(command_data, indent=2, ensure_ascii=False))

        self.TOTAL = command_data['total'] 
        self.TMP.append(command_data)
        
        while command_data['next'] is not None:
            query = urlparse(command_data['next']).query
            url_token = requests.get(cmd, params=query, headers=header)
            command_data = url_token.json()
            self.TMP.append(command_data)

            if not hide:
                json.dumps(command_data, indent=2, ensure_ascii=False)
                
        name_f = 'LikeSongs_saved.json'
        with open(name_f, 'w') as f:
            json.dump(self.TMP, f, ensure_ascii=False)
        print(LANGUAGE[set_LANG][11])
        
    def list_songs(self):
        ''' Show an enumarated list of the Liked Songs '''

        num = 1
        for i in self.TMP:
            for item in i['items']:
                print('{} {}: {}'.format(num, item['track']['artists'][0]['name'], item['track']['name']))
                num += 1

