#!/usr/bin/env python3

import argparse
import sys
from banner.Banner import banner

try:
    import requests
except:
    print("É preciso instalar a biblioteca requests")
    print()
    print("pip3 install requests")
    sys.exit()

try:
    from bs4 import BeautifulSoup
except:
    print("É preciso instalar a biblioteca beautifulsoup")
    print()
    print("pip install beautifulsoup4")
    sys.exit()

#Cores
R = '\033[31m'  # Vermelho
G = '\033[32m'  # Verde
END = '\033[0m'

fora = set()
noescopo = set()
verifica = set()

# Função que verifica arquivos no site
# Usado para verificar o robots.txt
def verifica_arquivo(url,file,silent=0):
    r = requests.get(f'{url}/{file}', headers=headers)
    if r.status_code == 200:
        if silent == 0:
            print(f'{G}[+] {file} existe{END}')
            print(f'[*] Conteúdo de {file}:')
            print()
            print(r.text)
        else:
            print(f'[*] Conteúdo de {file}:')
            print(r.text)

    else:
        print(f'{R}[-] {file} não existe{END}')

# Função que busca links presentes na página
def pega_links(url):
    r = requests.get(url, headers=headers)
    content = r.text
    
    soup = BeautifulSoup(content, 'html.parser')
    all_links = soup.find_all('a')

    links = set()
    for link in all_links:
        if "http" in link.get("href"):
            links.add(link.get("href"))
        else:
            links.add(f'{url}/{link.get("href")}')

    return links

# Função que verifica se os links encontrados estão disponíveis e se estão dentro do escopo
def verifica_links(links):
    for i in links:
        if i in noescopo:
            continue

        if args.target not in i:
            fora.add(i)
            continue

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
                    help='Deeping level for crawler (default: 0)'
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

if "http" not in args.target:
    url = f'http://{args.target}'
else:
    url = args.target

if not args.user_agent:
    headers = {'User-Agent': 'CrawAu'}
else:
    headers = {'User-Agent': args.user_agent}

try:
    r = requests.get(url, headers=headers)
except:
    print(f'{R}[-] Não é possível se conectar a {args.target}{END}')  
    sys.exit()  

if not args.quiet:
    print(banner.banner)
    print()
    print(f'[*] Conectando a {args.target}')
    print(f'{G}[+] Status Code {r.status_code}{END}')
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
    print(f"{R}[-] Nada encontrado!{END}")

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
    with open(file, 'w') as arquivo:
        for l in noescopo:
            arquivo.write(l+'\n')
