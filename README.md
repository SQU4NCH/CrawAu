# CrawAu
CrawAu é uma ferramenta de linha de comando em Python projetada para auxiliar em fases iniciais de recon. O objetivo é coletar informações sobre uma aplicação web de forma majoritariamente passiva, extraindo links, arquivos, verificando configurações comuns e buscando por potenciais vulnerabilidades ou informações expostas.

## Funcionalidades Principais

* **Verificação Inicial:** Testa a conectividade com o alvo, identifica o servidor web (se disponível via cabeçalho `Server`) e trata redirecionamentos.
* **Análise de `robots.txt`:** Verifica a existência e exibe o conteúdo do arquivo `robots.txt` para identificar diretórios que os administradores não desejam que sejam indexados.
* **Detecção de `.git` Exposto:** Tenta acessar o arquivo `.git/config` para verificar se um repositório Git está acidentalmente exposto no servidor web.
* **Crawling de Links:** Navega pela aplicação web a partir da URL inicial, extraindo links (`<a>` tags) encontrados nas páginas HTML.
    * **Controle de Profundidade:** Permite definir quantos "níveis" de links o crawler deve seguir a partir da página inicial (`-d` ou `--deep`).
    * **Separação de Escopo:** Diferencia links que pertencem ao domínio alvo (internos) de links que apontam para outros domínios (externos).
* **Extração de Arquivos JavaScript:** Identifica e extrai URLs de arquivos JavaScript (`<script src="...">`) referenciados nas páginas HTML visitadas.
* **Busca por Secrets:** Analisa o conteúdo dos arquivos JavaScript encontrados em busca de padrões que possam indicar informações sensíveis (chaves de API, tokens, etc.), utilizando expressões regulares definidas em `findsecrets.py`.
* **Enumeração de Subdomínios:** Tenta descobrir subdomínios válidos para o domínio alvo utilizando wordlist e verificando a resolução DNS.
* **Flexibilidade de User-Agent:** Permite usar um User-Agent padrão (`CrawAu/2.0`), um User-Agent aleatório de uma lista pré-definida (`--random-agent`), ou um User-Agent totalmente customizado.
* **Injeção de Headers:** Possibilita adicionar cabeçalhos HTTP customizados às requisições (ex: `Authorization`, `Cookie`) através da opção `--header`.
* **Modo Silencioso (`--quiet`):** Suprime a maioria das mensagens de status, exibindo apenas os resultados mais importantes ou erros.
* **Controle de Módulos:** Permite desativar verificações específicas como `robots.txt` (`--no-robots`), análise de JS (`--no-js`), enumeração de subdomínios (`--no-subs`) e verificação de `.git` (`--no-git-check`).
* **Saída para Arquivo:** Salva a lista de links internos encontrados em um arquivo de texto (`-o` ou `--output`).

## Instalação
1) ``git clone https://github.com/SQU4NCH/CrawAu``
2) ``cd CrawAu``
3) ``python3 -m pip install -r requirements.txt``
4) ``python3 crawau.py --help``

## Opções

```
usage: crawau.py [-h] [-d DEEP] [-q] [--random-agent] [--header HEADER] [--wordlist WORDLIST] [--no-robots] [--no-js] [--no-subs] [--no-git-check] [-o OUTPUT] target

CrawAu - Ferramenta de Reconhecimento Web Passivo

positional arguments:
  target                URL ou domínio alvo (ex: exemplo.com ou http://exemplo.com)

optional arguments:
  -h, --help            show this help message and exit
  -d DEEP, --deep DEEP  Nível de profundidade da varredura (default: 0)
  -q, --quiet           Suprimir a maioria das saídas (modo silencioso)
  --random-agent        Usar User-Agent aleatório da lista
  --header HEADER       Adicionar header customizado (Ex: "Authorization: Bearer token")
  --wordlist WORDLIST   Caminho para a wordlist de subdomínios (default: wordlist.txt)
  --no-robots           Não verificar o arquivo robots.txt
  --no-js               Não extrair e analisar arquivos JS
  --no-subs             Não enumerar subdomínios
  --no-git-check        Não verificar por repositório .git exposto
  -o OUTPUT, --output OUTPUT
                        Salvar links internos encontrados em um arquivo
```

## Exemplo

```
➜  CrawAu python3 crawau.py squ4nch.github.io --no-subs

    __________________
  <    CrawAu 2.0  >
    ------------------
                \   ^__^
                 \  (oo)\_______
                    (__)\       )\/\
                        ||-----||
                        ||     ||

    By: Squ4nch

--------------------------------------------------
[*] Alvo: http://squ4nch.github.io
[*] Domínio Base: squ4nch.github.io
[*] User-Agent: CrawAu/2.0
[*] Profundidade: 0
--------------------------------------------------
[*] Testando conexão com http://squ4nch.github.io...
[+] Conexão bem-sucedida (Status: 200)
[*] Redirecionado para: https://squ4nch.github.io/
[+] Servidor detectado: GitHub.com
[+] Arquivo 'robots.txt' encontrado (Status: 200).
[*] Conteúdo de robots.txt:
--------------------
Sitemap: https://squ4nch.github.io//sitemap.xml

--------------------
[*] Verificando se '.git/config' está exposto em https://squ4nch.github.io/
[*] Diretório '.git' não parece estar exposto (Status: 404 para .git/config).
[*] Iniciando extração de links e arquivos JS...
[*] Processando nível de profundidade: 0
[*] Analisando: https://squ4nch.github.io/
 -> https://www.instagram.com/ltxsecurity/ (Fora do escopo)
 -> https://squ4nch.github.io/write%20up/Internal/
 -> https://squ4nch.github.io/operating%20system/Sistema-Operacional/
 -> https://squ4nch.github.io/page3/
 -> https://www.linkedin.com/in/leo-teodoro/ (Fora do escopo)
 -> https://squ4nch.github.io/
 -> https://tryhackme.com/p/SQU4NCH (Fora do escopo)
 -> https://squ4nch.github.io/categories
 -> https://squ4nch.github.io/web%20hacking/HTTP-Request-Smuggling-new/
 -> https://squ4nch.github.io/mal%20dev/Entendendo-o-DLL-Hijacking/
 -> https://squ4nch.github.io/whoami
 -> https://github.com/SQU4NCH (Fora do escopo)
 -> https://twitter.com/SQU4NCH (Fora do escopo)
 -> https://squ4nch.github.io/bash/Customizando-bash-para-pentest/
 -> https://squ4nch.github.io/page7/
 -> https://squ4nch.github.io/page2/
 -> https://squ4nch.github.io/assets/js/clipboard.js
 -> https://squ4nch.github.io/assets/js/lunr/lunr-store.js
 -> https://squ4nch.github.io/assets/js/lunr/lunr.min.js
 -> https://cdn.jsdelivr.net/npm/clipboard@2/dist/clipboard.min.js (Fora do escopo)
 -> https://squ4nch.github.io/assets/js/lunr/lunr-en.js
 -> https://squ4nch.github.io/assets/js/main.min.js
 -> https://kit.fontawesome.com/4eee35f757.js (Fora do escopo)
[*] Fim da fase de crawling.
--------------------------------------------------
[*] Resumo do Crawling:
  Links Internos Encontrados (16):
    - https://squ4nch.github.io/write%20up/Internal/
    - https://squ4nch.github.io/operating%20system/Sistema-Operacional/
    - https://squ4nch.github.io/assets/js/clipboard.js
    - https://squ4nch.github.io/assets/js/lunr/lunr-store.js
    - https://squ4nch.github.io/page3/
    - https://squ4nch.github.io/assets/js/lunr/lunr.min.js
    - https://squ4nch.github.io/
    - https://squ4nch.github.io/categories
    - https://squ4nch.github.io/web%20hacking/HTTP-Request-Smuggling-new/
    - https://squ4nch.github.io/mal%20dev/Entendendo-o-DLL-Hijacking/
    - https://squ4nch.github.io/whoami
    - https://squ4nch.github.io/bash/Customizando-bash-para-pentest/
    - https://squ4nch.github.io/assets/js/lunr/lunr-en.js
    - https://squ4nch.github.io/page7/
    - https://squ4nch.github.io/assets/js/main.min.js
    - https://squ4nch.github.io/page2/
  Links Externos Encontrados (7):
    - https://www.instagram.com/ltxsecurity/
    - https://www.linkedin.com/in/leo-teodoro/
    - https://tryhackme.com/p/SQU4NCH
    - https://cdn.jsdelivr.net/npm/clipboard@2/dist/clipboard.min.js
    - https://twitter.com/SQU4NCH
    - https://github.com/SQU4NCH
    - https://kit.fontawesome.com/4eee35f757.js
  Arquivos JS Encontrados (5):
    - https://squ4nch.github.io/assets/js/clipboard.js
    - https://squ4nch.github.io/assets/js/lunr/lunr-store.js
    - https://squ4nch.github.io/assets/js/lunr/lunr.min.js
    - https://squ4nch.github.io/assets/js/main.min.js
    - https://squ4nch.github.io/assets/js/lunr/lunr-en.js
--------------------------------------------------
[*] Iniciando busca por informações sensíveis nos arquivos JS...
[*] Nenhuma informação sensível encontrada nos arquivos JS analisados.
[*] Execução concluída.
```
