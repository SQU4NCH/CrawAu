# CrawAu
Essa é uma ferramenta para coleta de informações web

A ideia é conseguir o maior número de informações sobre diretórios e subdomínios da aplicação sem realizar um Brute Force

A ferramenta "simula" a navegação de um usuário comum acessando a aplicação, dessa forma não chama a atenção dos mecanismos de defesa

Ela realiza uma consulta na URL passada e identifica todos os links presentes na página, após isso retorna todos os links que pertencem a esse domínio

Existe também a possibilidade de realizar uma consulta em profundidade, onde a ferramenta após descobrir os links, entra neles e realiza uma nova consulta

## Instalação
1) ``git clone https://github.com/SQU4NCH/CrawAu``
2) ``cd CrawAu``
3) ``python3 -m pip install -r requirements.txt``
4) ``python3 crawau.py --help``

## Opções

```
usage: crawau.py [-h] [-q] [-d DEEP] [-u USER_AGENT] [-o FILE_NAME] [--no-robots] target

positional arguments:
  target                Target url

options:
  -h, --help            show this help message and exit
  -q, --quiet           Suppress Output
  -d DEEP, --deep DEEP  Deeping level for crawler (default: 0)
  -u USER_AGENT, --user-agent USER_AGENT
                        User agent for requests (default: CrawAu)
  -o FILE_NAME, --output FILE_NAME
                        File to save the result
  --no-robots           Not look for robots.txt (default: no)
```

## Exemplo

```
➜ python3 crawau.py squ4nch.github.io

    __________________
  <    CrawAu 0.5.1  >
    ------------------
                \   ^__^
                 \  (oo)\_______
                    (__)\       )\/\
                        ||-----||
                        ||     ||

    By: Squ4nch
    

[*] Conectando a squ4nch.github.io
[+] Status Code 200
[*] Servidor: GitHub.com
[*] Verificando robots.txt
[+] robots.txt existe
[*] Conteúdo de robots.txt:

:)

[*] Extraindo links presentes na página

http://squ4nch.github.io/whoami.html
http://squ4nch.github.io/Certificações.html
http://squ4nch.github.io/index.html
http://squ4nch.github.io/Posts.html

[*] Encontrados mas possivelmente fora do escopo:

https://tryhackme.com/p/SQU4NCH
https://github.com/SQU4NCH
https://www.linkedin.com/in/leo-teodoro/

```
