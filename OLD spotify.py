import requests
from urllib.parse import urlencode
import base64
import datetime
import json
import os
import pyperclip

class spotify:
    token = 'https://accounts.spotify.com/api/token'
    authorize = 'https://accounts.spotify.com/authorize'
    file = './tokens/spotify_code.json'
    path = os.getenv('PYTHON_DEV')
    cred = os.path.join(path, './json/spotify.json')
    redirect = 'http://example.com/callback/'

    def __init__(self):
        self.agora = datetime.datetime.now()

        if os.path.exists(self.cred):
            with open(self.cred, 'r') as f:
                self.stored = json.load(f)
            if 'expired' in self.stored.keys() and 'refresh' in self.stored.keys():
                self.expired = self.agora > eval(self.stored['expires'])
            else:
                self.expired = None
                
            self.client_id = self.stored['client_id']
            self.client_secret = self.stored['client_secret']
            self.scope = self.stored['scope']
            self.refresh = self.stored['refresh']
            if 'code' in self.stored.keys():
                self.code = self.stored['code']
                print('Código de autorização já obtido!')
            else:
                self.authGet()
        else:
             self.authGet()

# ------------------------------ AUTENTICAÇÃO -------------

    def authGet(self, cod_expired=False):
        if not cod_expired and 'code' in self.stored.keys():
                return 'Não é necessário obter um novo código de autorização, já existe um'
        
        qsget = { 'client_id': self.client_id, 'response_type': 'code', 'redirect_uri': self.redirect, 'scope': self.scope }
        query_auth = urlencode(qsget)
        url_auth = f'{self.authorize}?{query_auth}'
        print(url_auth)
        self.auth_code = input('\nPressione ENTER quando houver copiado endereço inteiro')
        self.auth_code = pyperclip.paste()
        time_expire = self.agora + datetime.timedelta(seconds=3600)
        print('\nExpira em:', str(time_expire.time()))
        # O endereço deve ser copiado INTEIRO
        
        self.stored['code'] = self.auth_code.partition('=')[2]
        self.stored['expires'] = repr(time_expire)
        with open(self.cred, 'w') as f:
            json.dump(self.stored, f, indent=2)

        self.tokenGet()

    def insideToken(self, msg, refresh=False):
        if not refresh:
            auth = { 'grant_type': 'authorization_code', 'code': self.stored['code'] , 'redirect_uri': self.redirect }
        else:
            auth = { 'grant_type': 'refresh_token', 'refresh_token': self.stored['refresh'] }

        base = f'{self.client_id}:{self.client_secret}'
        base = bytes(base, 'UTF-8')
        basecode = base64.b64encode(base)
        basecode = basecode.decode('UTF-8')
        head = f'Basic {basecode}'
        header = { 'Authorization': head }
        
        url_token = requests.post(self.token, data=auth, headers=header)
        data = json.loads(url_token.text)
        print(json.dumps(data, indent=2))
        print(msg)
        print(url_token.status_code)

        if url_token.status_code != 200:
            print(f'ERRO: status code {url_token.status_code}')
            print(json.dumps(data, indent=2))
            if url_token.status_code == 400:
                self.cod_expired = True
                self.authGet(self.cod_expired)
        else:
            self.stored['refresh'] = data['refresh']
            self.stored['access_token'] = data['access_token']
            try:
                with open(self.cred, 'w') as f:
                    json.dump(self.stored, f, indent=2)
                print(json.dumps(self.stored, indent=2))
            except:
                print('Problemas gravando o arquivo JSON')
            print('Novo Token obtido!')

    def tokenGet(self):
        if self.refresh or self.expired:
            self.insideToken('\nRenovando Token...', refresh=True)
        if self.expired is None:
            self.insideToken('\nToken inexistente, obtendo novo token...')

    # --------------------------------- FUNÇÕES -------------

    def getSongs():
        ''' Baixar a playlista das minhas músicas salvas em SONGS '''
        global lista_dic
        offset = 0
        cmd = 'https://api.spotify.com/v1/me/tracks'
        bearer = 'Bearer ' + self.stored['access_token']
        header = { 'Authorization': bearer }
        query_get = { 'limit': 50, 'offset': offset }
        query = urlencode(query_get)
        url_token = requests.get(cmd, params=query, headers=header)
        command_data = json.loads(url_token.text)
        limite = command_data['total']
        lista_dic = []

        while offset < limite:
            cmd = 'https://api.spotify.com/v1/me/tracks'
            bearer = 'Bearer ' + self.stored['access_token']
            header = { 'Authorization': bearer }
            query_get = { 'limit': 50, 'offset': offset }
            query = urlencode(query_get)
            url_token = requests.get(cmd, params=query, headers=header)
            command_data = json.loads(url_token.text)
            lista_dic.append(command_data)

            print(json.dumps(command_data, indent=2))
            offset += 50

        name_f = 'spotify/saved.json'
        with open(name_f, 'w') as f:
            json.dump(lista_dic, f)
        print('SAVED SONGS salvas')

    def gerar_lista():
        file = open('spotify/saved.json')
        arquivo = open('spotify/preferidas', 'w')
        listas = json.load(file)

        global num
        num = 1
        for dic in listas:
            for lista in range(len(dic['items'])):
                song = dic['items'][lista]['track']['name']
                album = dic['items'][lista]['track']['album']['name']
                artist = dic['items'][lista]['track']['artists'][0]['name']

                forma = f'{num} {artist}: {song} ({album})\n'
                arquivo.write(forma)
                num += 1

        arquivo.close()
        file.close()
        print(f'\nLista GERADA! {num - 1} músicas no total')

    def commandApi():
        while True:
            # playlists = 'https://api.spotify.com/v1/me/playlists'
            cmd = input('\tCommand? ')
            bearer = 'Bearer ' + stored['access_token']
            header = { 'Authorization': bearer }
            query_get = { 'limit': 50, 'offset': '0' }
            query = urlencode(query_get)

            url_token = requests.get(cmd, params=query, headers=header)
            command_data = json.loads(url_token.text)
            print(json.dumps(command_data, indent=2))
            with open('spotify/data.json', 'w') as f:
                f.write(json.dumps(command_data, ensure_ascii=False, indent=2))

            continuar = input('Outro comando? s/n: ').lower()
            if 'n' in continuar:
                break
            elif 's' in continuar:
                continue
            else:
                print('Opção inválida, idiota')


    def gerenciador():
        while True:
            ask = input('\nT: Refresh Token\nC: Command\nS: Saved tracks\nG: Gerar lista a partir do JSON\nQ: Quit\n : ').lower()
            if 't' in ask:
                tokenGet()
            elif 'c' in ask:
                commandApi()
            elif 's' in ask:
                getSongs()
            elif 'g' in ask:
                gerar_lista()
            elif 'q' in ask:
                break
            else:
                print('Opção inválida, tente T ou C')

# Verificar se o Token está expirado, se estiver, recomeça a autenticação
# if expired or stored['code'] == "":
#     print('Token expirada')
#     authGet()
#     tokenGet()
#     gerenciador()
# else:
#     gerenciador()


