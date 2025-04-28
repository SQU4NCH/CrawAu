#!/usr/bin/env python3

import argparse
import sys
import socket
import requests
from bs4 import BeautifulSoup
import progressbar 

# Tenta importar módulos locais ou de bibliotecas
try:
    from banner.Banner import banner # Assumindo que está na estrutura correta
except ImportError:
    # Se não encontrar o banner, define uma string vazia ou uma simples
    class MockBanner:
        banner = "CrawAu Scanner"
    banner = MockBanner()

try:
    import useragent # Do arquivo useragent.py
except ImportError:
    print("[-] ERRO: Arquivo useragent.py não encontrado ou com erro.")
    # Define um user-agent padrão se o módulo falhar
    class MockUserAgent:
        random = 'CrawAu/2.0'
    useragent = MockUserAgent()

try:
    import findsecrets # Do arquivo findsecrets.py
except ImportError:
    print("[-] ERRO: Arquivo findsecrets.py não encontrado ou com erro.")
    # Define uma função mock se o módulo falhar
    class MockFindSecrets:
        def find_secrets(self, urls, headers):
            print("[-] Módulo findsecrets não carregado. Pulando busca por secrets.")
            return 0
    findsecrets = MockFindSecrets()


# Cores
R = '\033[31m'  # Vermelho
G = '\033[32m'  # Verde
Y = '\033[33m'  # Amarelo
END = '\033[0m'

# -- Variáveis Globais --
fora = set()
noescopo = set()
verifica = set()
js_files = set()

# -- Funções Auxiliares --

def print_info(msg):
    print(f'[*] {msg}')

def print_success(msg):
    print(f'{G}[+] {msg}{END}')

def print_warning(msg):
     print(f'{Y}[!] {msg}{END}')

def print_error(msg, exit_code=1):
    print(f'{R}[-] ERRO: {msg}{END}')
    if exit_code is not None:
        sys.exit(exit_code)

# -- Funções Principais --

def check_library(name, install_cmd):
    """Verifica se uma biblioteca está instalada e instrui como instalar."""
    try:
        __import__(name)
    except ImportError:
        print_error(f"Biblioteca '{name}' não encontrada.", exit_code=None)
        print(f"Instale usando: pip install {install_cmd}")
        sys.exit(1)

def configure_session(user_agent_string, custom_header_str=None):
    """Configura e retorna um objeto requests.Session com headers."""
    session = requests.Session()
    headers = {'User-Agent': user_agent_string}
    if custom_header_str:
        try:
            key, value = custom_header_str.split(":", 1)
            headers[key.strip()] = value.strip()
        except ValueError:
            print_error(f"Formato de header inválido: '{custom_header_str}'. Use 'Chave: Valor'.")
    session.headers.update(headers)
    return session

def verifica_arquivo(session, base_url, file_path, silent=False):
    """Verifica a existência e conteúdo de um arquivo específico (ex: robots.txt)."""
    target_url = f'{base_url.rstrip("/")}/{file_path.lstrip("/")}'
    try:
        r = session.get(target_url, timeout=10) # Adicionado timeout
        if r.status_code == 200:
            if not silent:
                print_success(f"Arquivo '{file_path}' encontrado (Status: {r.status_code}).")
                print(f"[*] Conteúdo de {file_path}:")
                print("-" * 20)
                print(r.text)
                print("-" * 20)
            return r.text # Retorna o conteúdo se encontrado
        else:
            if not silent:
                print_warning(f"Arquivo '{file_path}' não encontrado ou inacessível (Status: {r.status_code}).")
    except requests.exceptions.RequestException as e:
        if not silent:
            print_error(f"Erro ao tentar acessar '{target_url}': {e}", exit_code=None)
    return None

def verifica_git_exposed(session, base_url, silent=False):
    """Verifica se o diretório .git está exposto tentando acessar .git/config."""
    git_config_path = '.git/config'
    target_url = f'{base_url.rstrip("/")}/{git_config_path}'
    if not silent:
        print_info(f"Verificando se '{git_config_path}' está exposto em {base_url}")
    try:
        # HEAD=1 para evitar baixar o arquivo inteiro se for grande
        r = session.head(target_url, timeout=5, allow_redirects=False)
        
        if r.status_code != 200:
             r = session.get(target_url, timeout=5, allow_redirects=False, stream=True) # stream=True para ler só o necessário

        if r.status_code == 200:
             # Verifica se o conteúdo parece ser um arquivo config do git
             # Lendo apenas uma pequena parte para confirmação
             content_sample = r.raw.read(100).decode('utf-8', errors='ignore')
             if '[core]' in content_sample.lower():
                  print_success(f"Diretório '.git' POTENCIALMENTE EXPOSTO encontrado em {base_url} (Status: {r.status_code})!")
             else:
                  print_warning(f"Arquivo '{git_config_path}' encontrado, mas conteúdo não parece ser do git (Status: {r.status_code}).")
        else:
             if not silent:
                  print_info(f"Diretório '.git' não parece estar exposto (Status: {r.status_code} para {git_config_path}).")

    except requests.exceptions.RequestException as e:
        if not silent:
            print_error(f"Erro ao verificar '{target_url}': {e}", exit_code=None)


def normaliza_link(base_url, link_href):
    """Constroi uma URL absoluta a partir de um href."""
    if not link_href:
        return None
    # Ignora âncoras, javascript:, mailto:, etc.
    if link_href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
        return None
    # Se já for absoluto
    if link_href.startswith(('http://', 'https://')):
        return link_href
    # Se for relativo ao protocolo
    if link_href.startswith('//'):
        protocolo = base_url.split(':')[0]
        return f"{protocolo}:{link_href}"
    # Se for relativo à raiz
    if link_href.startswith('/'):
        base_domain = '/'.join(base_url.split('/')[:3])
        return f"{base_domain}{link_href}"
    # Se for relativo ao diretório atual
    base_dir = base_url.rsplit('/', 1)[0]
    return f"{base_dir}/{link_href}"

def extrai_elementos(session, url, tag, atributo_src):
    """Extrai URLs de um atributo específico de uma tag HTML."""
    elementos = set()
    try:
        r = session.get(url, timeout=10)
        r.raise_for_status() # Levanta erro para status ruins (4xx, 5xx)
        content = r.text
        soup = BeautifulSoup(content, 'html.parser')
        tags = soup.find_all(tag)

        for item in tags:
            src = item.get(atributo_src)
            url_absoluta = normaliza_link(url, src)
            if url_absoluta:
                elementos.add(url_absoluta)

    except requests.exceptions.RequestException as e:
        print_error(f"Erro ao buscar elementos '{tag}' em {url}: {e}", exit_code=None)
    except Exception as e:
        print_error(f"Erro ao parsear HTML de {url}: {e}", exit_code=None)

    return elementos

def verifica_escopo(links_encontrados, target_domain):
    """Separa links dentro e fora do escopo e atualiza sets globais."""
    novos_no_escopo = set()
    for link in links_encontrados:
        # Evita reprocessar links já vistos
        if link in noescopo or link in fora or link in verifica:
            continue

        if target_domain in link.split('/')[2]: # Verifica o domínio base
            if link not in noescopo:
                print(f"{G} -> {link}{END}") # Mostra link interno encontrado
                noescopo.add(link)
                novos_no_escopo.add(link)
        else:
            if link not in fora:
                print(f"{Y} -> {link} (Fora do escopo){END}") # Mostra link externo
                fora.add(link)
    return novos_no_escopo


def sub_finder(target_domain, wordlist_path):
    """Enumera subdomínios usando uma wordlist."""
    print_info(f"Iniciando enumeração de subdomínios para {target_domain}...")
    print_info(f"Usando wordlist: {wordlist_path}")
    find_count = 0
    try:
        with open(wordlist_path, "r") as lst:
            # Lê as linhas e remove espaços/quebras de linha
            subdomains = [line.strip() for line in lst if line.strip()]

        # Setup progressbar
        bar = progressbar.ProgressBar(max_value=len(subdomains), redirect_stdout=True)

        for i, sub in enumerate(subdomains):
            bar.update(i + 1)
            sub_url = f"{sub}.{target_domain}"
            try:
                ip = socket.gethostbyname(sub_url)
                print(f"{G}[+] Subdomínio encontrado: {sub_url}\t{ip}{END}")
                find_count += 1
            except socket.gaierror:
                continue # Não encontrado, continua silenciosamente
            except Exception as e:
                print_error(f"Erro ao resolver {sub_url}: {e}", exit_code=None)
        bar.finish()

    except FileNotFoundError:
        print_error(f"Wordlist não encontrada em '{wordlist_path}'")
        return # Não pode continuar sem wordlist
    except Exception as e:
        print_error(f"Erro durante a enumeração de subdomínios: {e}", exit_code=None)


    if find_count == 0:
        print_warning(f"Nenhum subdomínio encontrado com a wordlist fornecida.")
    else:
        print_success(f"{find_count} subdomínio(s) encontrado(s).")


# -- Main Execution --
if __name__ == "__main__":
    # Verificar bibliotecas essenciais
    check_library("requests", "requests")
    check_library("bs4", "beautifulsoup4")
    check_library("progressbar", "progressbar2")

    # Configuração do argparse
    parser = argparse.ArgumentParser(description="CrawAu - Ferramenta de Reconhecimento Web Passivo")
    parser.add_argument('target', help='URL ou domínio alvo (ex: exemplo.com ou http://exemplo.com)')
    parser.add_argument('-d', '--deep', type=int, default=0, help='Nível de profundidade da varredura (default: 0)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suprimir a maioria das saídas (modo silencioso)')
    parser.add_argument('--random-agent', action='store_true', help='Usar User-Agent aleatório da lista')
    parser.add_argument('--header', help='Adicionar header customizado (Ex: "Authorization: Bearer token")')
    parser.add_argument('--wordlist', default='wordlist.txt', help='Caminho para a wordlist de subdomínios (default: wordlist.txt)')
    parser.add_argument('--no-robots', action='store_true', help='Não verificar o arquivo robots.txt')
    parser.add_argument('--no-js', action='store_true', help='Não extrair e analisar arquivos JS')
    parser.add_argument('--no-subs', action='store_true', help='Não enumerar subdomínios')
    parser.add_argument('--no-git-check', action='store_true', help='Não verificar por repositório .git exposto')
    parser.add_argument('-o', '--output', help='Salvar links internos encontrados em um arquivo')

    args = parser.parse_args()

    # Define o URL base
    if not args.target.startswith(('http://', 'https://')):
        base_url = f'http://{args.target}'
        target_domain = args.target
    else:
        base_url = args.target
        target_domain = base_url.split('/')[2] # Extrai o domínio da URL

    # Define o User-Agent
    user_agent_str = useragent.random if args.random_agent else 'CrawAu/2.0'

    # Configura a sessão requests
    session = configure_session(user_agent_str, args.header)

    if not args.quiet:
        print(banner.banner) # Mostra o banner se existir
        print("-" * 50)
        print_info(f"Alvo: {base_url}")
        print_info(f"Domínio Base: {target_domain}")
        print_info(f"User-Agent: {session.headers['User-Agent']}")
        if args.header:
            print_info(f"Header Adicional: {args.header}")
        print_info(f"Profundidade: {args.deep}")
        print("-" * 50)

    # Verifica conexão inicial
    try:
        print_info(f"Testando conexão com {base_url}...")
        r = session.head(base_url, timeout=10, allow_redirects=True) 
        r.raise_for_status()
        print_success(f"Conexão bem-sucedida (Status: {r.status_code})")
        final_url = r.url # Pega a URL final após redirecionamentos
        if final_url != base_url:
             print_info(f"Redirecionado para: {final_url}")
             base_url = final_url # Atualiza o base_url se houve redirecionamento
             target_domain = base_url.split('/')[2] # Atualiza o domínio se necessário
        try:
            server = r.headers.get('Server')
            if server and not args.quiet:
                print_success(f"Servidor detectado: {server}")
        except:
            pass
    except requests.exceptions.RequestException as e:
        print_error(f"Não foi possível conectar a {base_url}: {e}")
        # Não adianta continuar se não conectar
        sys.exit(1)

    # --- Verificações Iniciais ---
    if not args.no_robots:
        verifica_arquivo(session, base_url, "robots.txt", args.quiet)

    if not args.no_git_check:
        verifica_git_exposed(session, base_url, args.quiet) 

    # --- Crawling ---
    print_info("Iniciando extração de links e arquivos JS...")
    urls_para_visitar = {base_url} # Começa com a URL base
    links_processados = set() # Links já visitados para evitar loops

    for nivel_atual in range(args.deep + 1):
        if not urls_para_visitar:
            break # Sai se não houver mais URLs para visitar

        if not args.quiet:
            print_info(f"Processando nível de profundidade: {nivel_atual}")

        novos_links_neste_nivel = set()
        urls_a_processar_neste_nivel = urls_para_visitar.copy()
        urls_para_visitar.clear() # Limpa para a próxima iteração

        for url in urls_a_processar_neste_nivel:
            if url in links_processados:
                continue # Já processou esta URL
            links_processados.add(url)

            if not args.quiet:
                print_info(f"Analisando: {url}")

            # Extrai links <a>
            links_pagina = extrai_elementos(session, url, 'a', 'href')
            novos_internos = verifica_escopo(links_pagina, target_domain)
            novos_links_neste_nivel.update(novos_internos) # Adiciona novos links internos para o próximo nível

            # Extrai links <script>
            if not args.no_js:
                scripts_pagina = extrai_elementos(session, url, 'script', 'src')
                # Verifica escopo dos scripts e adiciona aos sets globais
                verifica_escopo(scripts_pagina, target_domain)
                # Adiciona os JS encontrados ao set específico js_files
                for script_url in scripts_pagina:
                    if target_domain in script_url.split('/')[2]: # Apenas JS do domínio alvo
                         js_files.add(script_url)

        # Prepara as URLs para o próximo nível de profundidade
        urls_para_visitar = novos_links_neste_nivel - links_processados

    print_info("Fim da fase de crawling.")

    # --- Resultados do Crawling ---
    if not args.quiet:
        print("-" * 50)
        print_info("Resumo do Crawling:")
        print(f"  Links Internos Encontrados ({len(noescopo)}):")
        # Limita a exibição para não poluir muito
        for i, link in enumerate(list(noescopo)[:20]): print(f"    - {link}")
        if len(noescopo) > 20: print(f"    ... e mais {len(noescopo)-20}")

        print(f"  Links Externos Encontrados ({len(fora)}):")
        for i, link in enumerate(list(fora)[:10]): print(f"    - {link}")
        if len(fora) > 10: print(f"    ... e mais {len(fora)-10}")

        if not args.no_js:
             print(f"  Arquivos JS Encontrados ({len(js_files)}):")
             for i, js in enumerate(list(js_files)[:10]): print(f"    - {js}")
             if len(js_files) > 10: print(f"    ... e mais {len(js_files)-10}")
        print("-" * 50)


    # --- Análise de Secrets em JS ---
    if not args.no_js and js_files:
        print_info("Iniciando busca por informações sensíveis nos arquivos JS...")
        try:
            result_count = findsecrets.find_secrets(js_files, session.headers)
            if result_count == 0:
                print_info("Nenhuma informação sensível encontrada nos arquivos JS analisados.")
            else:
                print_success(f"{result_count} potenciais segredos encontrados nos arquivos JS.")
        except AttributeError:
             print_error("Função 'find_secrets' não encontrada no módulo 'findsecrets'. Verifique o arquivo findsecrets.py.")
        except Exception as e:
            print_error(f"Erro ao buscar secrets nos arquivos JS: {e}", exit_code=None)


    # --- Enumeração de Subdomínios ---
    if not args.no_subs:
        sub_finder(target_domain, args.wordlist)

    # --- Salvar Resultados ---
    if args.output:
        print_info(f"Salvando links internos em '{args.output}'...")
        try:
            with open(args.output, 'w') as f:
                for link in sorted(list(noescopo)): # Salva ordenado
                    f.write(link + '\n')
            print_success(f"Links internos salvos com sucesso em '{args.output}'.")
        except Exception as e:
            print_error(f"Não foi possível salvar o arquivo '{args.output}': {e}", exit_code=None)

    print_info("Execução concluída.")
