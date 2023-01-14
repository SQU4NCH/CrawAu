# CrawAu
Essa é uma ferramenta para coleta de informações web

A ferramenta realiza uma consulta na URL passada e identifica todos os links presentes na página que estão ativos, após isso retorna todos os links que pertencem ao domínio passado

Existe também a possibilidade de realizar uma consulta em profundidade, onde a ferramenta após descobrir os links, entra neles e realiza uma nova consulta

A ideia é conseguir o maior número de informações sobre diretórios e subdomínios da aplicação sem realizar um Brute Force

## Opções

```
usage: crawau.py [-h] [-q] [-d DEEP] [-u USER_AGENT] [-o FILE_NAME] target

positional arguments:
  target                Target url

optional arguments:
  -h, --help            show this help message and exit
  -q, --quiet           Suppress Output
  -d DEEP, --deep DEEP  Deeping level for crawler
  -u USER_AGENT, --user-agent USER_AGENT
                        User agent for requests, default = CrawAu
  -o FILE_NAME, --output FILE_NAME
                        File to save the result
```

## Exemplo

```
➜ python3 crawau.py google.com

  __________________
<       Craw Au      >
  ------------------
            \   ^__^
             \  (oo)\_______
                (__)\       )\/\
                    ||----w |
                    ||     ||

 By: Squ4nch

[*] Conectando a google.com
[+] Status Code 200
[*] Verificando robots.txt
[+] robots.txt existe
[*] Conteúdo de robots.txt:

User-agent: *
Disallow: /search
Allow: /search/about
Allow: /search/static
Allow: /search/howsearchworks
Disallow: /sdch
.
.
.
Sitemap: https://www.google.com/sitemap.xml

[*] Extraindo links presentes na página

http://www.google.com/setprefdomain?prefdom=BR&amp;prev=http://www.google.com.br/&amp;sig=K_HS5DP6gHnHe2ZnMCtzBNY8sHqrU%3D
https://accounts.google.com/ServiceLogin?hl=pt-BR&passive=true&continue=http://www.google.com/&ec=GAZAAQ
http://www.google.com.br/history/optout?hl=pt-BR
http://www.google.com.br/imghp?hl=pt-BR&tab=wi
https://news.google.com/?tab=wn
http://maps.google.com.br/maps?hl=pt-BR&tab=wl
https://mail.google.com/mail/?tab=wm
https://play.google.com/?hl=pt-BR&tab=w8
https://www.google.com.br/intl/pt-BR/about/products?tab=wh
https://drive.google.com/?tab=wo

[*] Encontrados mas possivelmente fora do escopo:

https://www.youtube.com/?tab=w1

```
