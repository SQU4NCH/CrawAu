#!/usr/bin/env python3

import argparse
import sys
from banner.Banner import banner
import useragent
import socket
import findsecrets

#Cores
R = '\033[31m'  # Vermelho
G = '\033[32m'  # Verde
END = '\033[0m'

def error(msg):
    print(f'{R}[-] ERRO: {msg}{END}')
    sys.exit(1)

try:
    import progressbar
except:
    print("É preciso instalar a biblioteca progressbar")
    print()
    print("pip3 install progressbar2")
    sys.exit()

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
        try:
            if "http" in link.get("href"):
                links.add(link.get("href"))
            else:
                if link.get("href")[0] == "/":
                    links.add(f'{url}{link.get("href")}')
                    continue
                links.add(f'{url}/{link.get("href")}')
        except:
            continue

    return links

# Função que busca arquivos .js presentes na página
def enum_js(url):
    r = requests.get(url, headers=headers)
    content = r.text
    
    soup = BeautifulSoup(content, 'html.parser')
    all_links = soup.find_all('script')

    js = set()
    for link in all_links:
        try:
            if "http" in link.get("src"):
                js.add(link.get("src"))
            else:
                if link.get("src")[0] == "/":
                    js.add(f'{url}{link.get("src")}')
                    continue
                js.add(f'{url}/{link.get("src")}')
        except:
            continue
    return js

# Função que verifica se os links encontrados estão dentro do escopo
def verifica_links(links):
    for i in links:
        if i in noescopo:
            continue

        if args.target not in i:
            fora.add(i)
            continue

        noescopo.add(i)
        print(i)

# Função que enumera subdomínios de forma passiva
def subFind(url):
    find = 0
    with open("./wordlist.txt", "r") as lst:
        for i in progressbar.progressbar(lst, redirect_stdout=True):  
            i = i.rstrip("\n")
            SubUrl = f"{i}.{url}"
            try:
                ip = socket.gethostbyname(SubUrl)
                print(f"{SubUrl}\t{ip}")
                find += 1
            except:
                continue

    if find == 0:
        print(f"{R}[-] Nenhum subdominio encontrado{END}")

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
parser.add_argument('-d',
                    dest='deep',
                    help='Deeping level for crawler (default: 0)'
                    )
parser.add_argument('--random-agent',
                    action='store_true',
                    dest='random_agent',
                    help='Random user agent for requests (default: CrawAu)'
                    )
parser.add_argument('-o', 
                    dest='file_name',
                    help='File to save the result'
                    )
parser.add_argument('--no-robots',
                    action='store_true',
                    dest='norobots',
                    help='Not look for robots.txt (default: no)'
                    )
parser.add_argument('--no-js',
                    action='store_true',
                    dest='nojs',
                    help='Not look for js files (default: no)'
                    )
parser.add_argument('--header',
                    dest='header',
                    help='header key:value (Ex: "Authorization: Basic YWxhZGRpbjpvcGVuc2VzYW1l")'
                    )                     
args = parser.parse_args()

file = args.file_name
deep = args.deep

if "http" not in args.target:
    url = f'http://{args.target}'
else:
    url = args.target

if not args.header:
    if not args.random_agent:
        headers = {'User-Agent': 'CrawAu'}
    else:
        headers = {'User-Agent': useragent.random}
else:
    h = args.header.split(":")
    if not args.random_agent:
        headers = {'User-Agent': 'CrawAu', h[0]: h[1].lstrip()}
    else:
        headers = {'User-Agent': useragent.random, h[0]: h[1].lstrip()}

try:
    r = requests.get(url, headers=headers)
except:
    error(f'Não é possível se conectar a {args.target}') 

if not args.quiet:
    print(banner.banner)
    print()
    if args.header:
        print(f'[*] Headers: {args.header}')
    if args.random_agent:
        print(f'[*] User-Agent: {useragent.random}')
    print(f'[*] Conectando a {args.target}')
    print(f'{G}[+] Status Code {r.status_code}{END}')
    try:
        servidor = r.headers['Server']
        print(f"{G}[+] Servidor: {servidor}{END}")
    except:
        pass
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

# Faz a busca dos arquivos JS e depois busca por informações sensíveis
if not args.nojs:
    print("[*] Extraindo arquivos JS presentes na página")
    script = enum_js(url)
    print()
    if len(script) == 0:
        print(f"{R}[-] Nada encontrado!{END}")
    else:
        verifica_links(script)
        print()

        print("[*] Buscando por informações sensíveis nos arquivos JS")

        try:
            result = findsecrets.find_secrets(script, headers)

            if result == 0:
                print()
                print(f"{R}[-] Nada encontrado!{END}")

            print()
        except:
            print(f"{R}[-] Não foi possível extrair o conteúdo dos arquivos JS{END}")


contr = 0
while contr != 1:
    isSub = input("[*] Você deseja enumerar subdominios? [S/n] ")

    if isSub.lower() == 'n':
        sys.exit(1)

    if isSub == '' or isSub.lower() == 's':
        contr = 1

print("[*] Enumerando possiveis subdominios e seus IPs de forma passiva")
print("[*] Isso pode demorar um pouco...")
print()
urlClean = url.split('/')[2]
subFind(urlClean)

# Salva os links do escopo em um arquivo
if args.file_name:
    with open(file, 'w') as arquivo:
        for l in noescopo:
            arquivo.write(l+'\n')
