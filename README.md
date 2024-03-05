# CrawAu
Essa é uma ferramenta para coleta de informações web

A ideia é conseguir o maior número de informações sobre diretórios e subdomínios da aplicação sem realizar um Brute Force

A ferramenta "simula" a navegação de um usuário comum acessando a aplicação, dessa forma não chama a atenção dos mecanismos de defesa

Ela realiza uma consulta na URL passada e identifica todos os links presentes na página, após isso retorna todos os links que pertencem a esse domínio

Existe também a possibilidade de realizar uma consulta em profundidade, onde a ferramenta após descobrir os links, entra neles e realiza uma nova consulta

Além dos links, a ferramenta também retorna todos os arquivos JavaScript presentes na URL e também realiza buscas por informações sensíveis dentro deles, como por exemplo, chaves de API, secrets, entre outros

Outra função disponível na ferramenta é a descoberta de subdomínios da aplicação, sem que seja necessário realizar um brute force.

## Instalação
1) ``git clone https://github.com/SQU4NCH/CrawAu``
2) ``cd CrawAu``
3) ``python3 -m pip install -r requirements.txt``
4) ``python3 crawau.py --help``

## Opções

```
usage: crawau.py [-h] [-q] [-d DEEP] [--random-agent] [-o FILE_NAME] [--no-robots] [--no-js] [--header HEADER] target

positional arguments:
  target           Target url

options:
  -h, --help       show this help message and exit
  -q, --quiet      Suppress Output
  -d DEEP          Deeping level for crawler (default: 0)
  --random-agent   Random user agent for requests (default: CrawAu)
  -o FILE_NAME     File to save the result
  --no-robots      Not look for robots.txt (default: no)
  --no-js          Not look for js files (default: no)
  --header HEADER  header key:value (Ex: "Authorization: Basic YWxhZGRpbjpvcGVuc2VzYW1l")
```

## Exemplo

```
➜  CrawAu python3 crawau.py squ4nch.github.io

    __________________
  <    CrawAu 1.5.0  >
    ------------------
                \   ^__^
                 \  (oo)\_______
                    (__)\       )\/\
                        ||-----||
                        ||     ||

    By: Squ4nch
    

[*] Conectando a squ4nch.github.io
[+] Status Code 200
[+] Servidor: GitHub.com
[*] Verificando robots.txt
[+] robots.txt existe
[*] Conteúdo de robots.txt:

Sitemap: https://squ4nch.github.io//sitemap.xml


[*] Extraindo links presentes na página

http://squ4nch.github.io/cheatsheet
http://squ4nch.github.io/categories
http://squ4nch.github.io/review/Minha-experiencia-com-a-eMAPT/
http://squ4nch.github.io/page3/
http://squ4nch.github.io/#main
http://squ4nch.github.io/page2/
http://squ4nch.github.io/notes/Arquitetura/
http://squ4nch.github.io/whoami
http://squ4nch.github.io/notes/Assembly/
http://squ4nch.github.io/#site-nav
http://squ4nch.github.io/write%20up/CSSB2019/
http://squ4nch.github.io/page5/
http://squ4nch.github.io/page4/
http://squ4nch.github.io/notes/XSS-Evasion/
http://squ4nch.github.io/#footer
http://squ4nch.github.io/#
http://squ4nch.github.io/

[*] Encontrados mas possivelmente fora do escopo:

https://www.linkedin.com/in/leo-teodoro/
https://tryhackme.com/p/SQU4NCH
https://github.com/SQU4NCH
https://www.instagram.com/ltxsecurity/

[*] Extraindo arquivos JS presentes na página

http://squ4nch.github.io/assets/js/lunr/lunr.min.js
http://squ4nch.github.io/assets/js/lunr/lunr-en.js
http://squ4nch.github.io/assets/js/lunr/lunr-store.js
http://squ4nch.github.io/assets/js/clipboard.js
http://squ4nch.github.io/assets/js/main.min.js

[*] Buscando por informações sensíveis nos arquivos JS

[-] Nada encontrado!

[*] Você deseja enumerar subdominios? [S/n] n
```
