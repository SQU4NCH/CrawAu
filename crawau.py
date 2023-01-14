#!/usr/bin/env python3

import argparse
import re
import sys

try:
    import requests
except:
    print("É preciso instalar a biblioteca requests")
    print()
    print("pip3 install requests")
    sys.exit()

fora = set()
noescopo = set()
verifica = set()

# Função que verifica arquivos no site
# Usado para verificar o robots.txt
def verifica_arquivo(url,file,silent=0):
    r = requests.get(f'{url}/{file}', headers=headers)
    if r.status_code == 200:
        if silent == 0:
            print(f'\033[2;32m[+] {file} existe\033[0;0m')
            print(f'[*] Conteúdo de {file}:')
            print()
            print(r.text)
        else:
            print(f'[*] Conteúdo de {file}:')
            print(r.text)

    else:
        print(f'\033[2;31m[-] {file} não existe\033[0;0m')

# Função que busca links presentes na página
def pega_links(url):
    r = requests.get(url, headers=headers)
    content = r.text
    links = set(re.findall(r'(?<=href=["\'])https?://.+?(?=["\'])', content))

    return links

# Função que verifica se os links encontrados estão disponíveis e se estão dentro do escopo
def verifica_links(links):
    for i in links:
        if i in noescopo:
            continue

        if args.target not in i:
            fora.add(i)
            continue

        valida = requests.get(i, headers=headers)
        if valida.status_code == 200:
            noescopo.add(i)
            print(i)

# Menu de ajuda
parser = argparse.ArgumentParser()
parser.add_argument('-q', '--quiet',
                    action='store_true',
                    dest='quiet',
                    help='Suppress Output'
                    )
parser.add_argument('target',
                    help='Target url'
                    )
parser.add_argument('-d', '--deep',
                    dest='deep',
                    help='Deeping level for crawler'
                    )
parser.add_argument('-u', '--user-agent',
                    dest='user_agent',
                    help='User agent for requests (default: CrawAu)'
                    )
parser.add_argument('-o', '--output',
                    dest='file_name',
                    help='File to save the result'
                    )
parser.add_argument('--no-robots',
                    action='store_true',
                    dest='norobots',
                    help='Not look for robots.txt (default: no)'
                    )                      
args = parser.parse_args()

file = args.file_name
deep = args.deep
url = f'http://{args.target}'

if not args.user_agent:
    headers = {'User-Agent': 'CrawAu'}
else:
    headers = {'User-Agent': args.user_agent}

try:
    r = requests.get(url, headers=headers)
except:
    print(f'\033[2;31m[-] Não é possível se conectar a {args.target}\033[0;0m')  
    sys.exit()  

if not args.quiet:
    print("""
  __________________
<       Craw Au      >
  ------------------
            \   ^__^
             \  (oo)\_______
                (__)\       )\/\\
                    ||----w |
                    ||     ||

\033[2;34m By: Squ4nch\033[0;0m
    """)
    print()
    print(f'[*] Conectando a {args.target}')
    print(f'\033[2;32m[+] Status Code {r.status_code}\033[0;0m')
    if not args.norobots:
        print('[*] Verificando robots.txt')
        verifica_arquivo(url,"robots.txt")
        print()
    print('[*] Extraindo links presentes na página')
else:
    if not args.norobots:
        verifica_arquivo(url,"robots.txt",1)

if not deep:
    links = pega_links(url)
    print()
    verifica_links(links)
else:
    if not args.quiet:
        print(f'[*] Profundidade {deep}')
        print() 
    
    links = pega_links(url)
    verifica_links(links)
    
    # Loop responsável por entrar nos links e buscar novos links
    for n in range(0,int(deep)):
        novo = noescopo - verifica
        verifica = noescopo.copy()
        for i in novo:
            links = pega_links(i)
            verifica_links(links)

if len(noescopo) == 0:
    print("\033[2;31m[-] Nada encontrado!\033[0;0m")

# Retorna os links que aparentemente estão fora do escopo
# Necessário para validar se realmente está fora do escopo
if not args.quiet:
    print()
    print("[*] Encontrados mas possivelmente fora do escopo:")
    print()
    print(*fora, sep='\n')
    print()

# Salva os links do escopo em um arquivo
if args.file_name:
    arquivo = open(file, 'w')
    for l in noescopo:
        arquivo.write(l+'\n')
    arquivo.close