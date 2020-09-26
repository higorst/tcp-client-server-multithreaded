# A Multithreaded TCP Server-Client Implementation
###### With cache memory

***

> Higor Santos de Jesus <br>
> Bachelor of Exact and Technological Sciences - UFRB <br>
> Graduating in Computer Engineering - UFRB <br>

- [Overview](#overview)
- [Server](#server)
- [Client](#client)
- [Package Sending and Receiving](#packages)
- [Multi-Thread Implementation](#multithread)
- [Cache Implementation](#cache)
- [File Access](#file)
- [Results](#results)

#### <a id="overview" />Overview

Esse proejto descreve a implementação de um cliente TCP, que recupera arquivos de um determinado diretório ao estabelecer uma conexão com um servidor TCP, bem como obter uma lista dos arquivos armazenados na memória cache do mesmo. A memória cache do servidor possui um limite máximo de 64 MB, bem como o buffer de transferência de pacotes um limite de 1024 bytes. Após estabelecer uma conexão com o servidor, o cliente envia uma requisição com o nome do arquivo que deseja recuperar ou método de listagem dos arquivos. O servidor por sua vez corresponde a solitação do cliente de acordo com o método invocado. Quando solicitada a lista de arquivos, é retornada a relação de arquivos armazenados na cache. Quando é solicitado um arquivo, são realizadas as seguintes etapas: 
- Verifica a exisitência do arquivo no diretório do qual o servidor está direcionado;
- Verifica se o arquivo está presente na memória cache;
    - Se o arquivo não estiver na memória cache o servidor tentará alocar esse arquivo:
        - Será verificado o espaço disponível para alocação de um novo arquivo;
        - Arquivos serão removidos da memória para liberar espaço, quando necessário;
        - O arquivo será serializado em pacotes, de acordo com o tamanho do buffer de transição;
    - Se o arquivo está presente, é feito o envio do mesmo para o requerente;
    - Ser o arquivo possuir tamanho superior ao limite máximo da cache (64MB), ele não é alocado para a memória;
- Envia o arquivo quando disponível;

#### <a id="server" />Server

O servidor TCP exige um padrão em sua execução, de acordo com o seguintes parâmetros:
```sh
$ python3 tcp_server.py host port directory_to_access
```
Sendo definidos pelo usuário:
- __host:__ o endereço ip de conexão, do qual será acessado pelo cliente.
    - _ex:_ localhost or 127.0.0.1
- __port:__ a porta de conexão, da qual será acessada pelo cliente.
    - _ex:_ 3000 
- __directory_to_access:__ diretório do qual serão acessados os arquivos.
    - _._ or _./_ para diretório local
    - _ex:_ docs/images/  

#### <a id="client" />Client

O client TCP exige um padrão em sua execução a depender da necessidade do usuário, de acordo com as seguintes variações de parâmetros:
```sh
$ python3 tcp_client.py host port file_name directory_to_save
or
$ python3 tcp_client.py host port list
```
Sendo definidos pelo usuário:
- __host:__ o endereço ip de conexão, deve ser o mesmo definido no tcp_server.
    - _ex:_ localhost or 127.0.0.1
- __port:__ a porta de conexão, deve ser a mesma definida no tcp_server.
    - _ex:_ 3000 
- __file_name:__ arquivo que se deseja recuperar do servidor.
    - _ex:_ movie.mp4, market_list.docx 
- __directory_to_save:__ diretório do qual serão acessados os arquivos.
    - _._ or _./_ para diretório local
    - _ex:_ files/receives/documents/  
- __list:__ deve ser mantida essa nomenclatura. Serve para requisitar a lista de arquivos presente na memória cache do servidor.

#### <a id="packages" />Package Sending and Receiving

O processo de recuperação de arquivos, é feito basicamente pelo envio de pacotes do servidor para o cliente. No servidor quando um arquivo é acessado ele é serializado em formato de pacotes, de acordo com o tamanho do buffer de envio. Esses pacotes a medida que vão sendo recebidos pelo cliente, são unidos para formar o arquivo no diretório escolhido pelo usuário.

O código abaixo exibe as etapas e serialização e desserialização, a partir da leitura e escrita do arquivo.

```python
# servidor serializa os dados e envia os pacotes
with open(dir + res2, OPEN_FILE_SERVER) as f:
  package = f.read(BUFFER_SIZE)
  while package:
      # sending file packages
      c.send(package)
      package = f.read(BUFFER_SIZE)
  f.close()

# cliente recebe os pacotes que compõe o arquivo
with open(receive_f, OPEN_FILE_CLIENT) as f:
  package = s.recv(BUFFER_SIZE)
  while package:
      f.write(package)
      package = s.recv(BUFFER_SIZE)
  f.close()
```

#### <a id="multithread" />Multi-Thread Implementation

O servidor TCP permite a conexão de mais um cliente por vez, ou seja, diferentes clientes que estabeleçam uma conexão com o servidor podem solicitar arquivos ou a listagem dos presentes na memória cache. Uma abstração dessa topologia de conexõa pode ser observada na figura abaixo:

<div style="text-align:center"><img src="/assets/server_client_tcp.png" /></div>

Esse funcionamento se resume a maneira com a qual o servidor aguarda novas conexões. O canal de comunicação entre servidor e cliente, denominado socket, fica aguardando uma novação conexão e quando essa é estabelecida, o servidor aloca a mesma como uma thread e fica aguardando outras. Tornando assim, possível que vários clientes possa requisitar arquivos do servidor sem a necessidade de aguardar o fim de uma outra conexão.

#### <a id="cache" />Cache Implementation

A memória cache é construída a partir de uma estrutura de tabela hash, o dictionary do Python, do qual possui para cada posição uma chave e um conteúdo associado a mesma. Sua construção no server TCP, se baseia da seguinte forma:

- A chave definida pelo nome do arquivo;
- O conteúdo da chave, composto por três informações:
  - file_size: o tamanho do arquivo;
  - file_packages: a serialização do arquivo por pacotes de envio, de acordo com o tamanho do buffer do socket;
  - lock: uma flag que identifica se o arquivo está sendo consultado ou não por um cliente.

Quando um arquivo é adicionado a memória cache, o servidor o associa da forma citada anteriormente. Vale destacar a importância do conteúdo 'lock', responsável por assegurar que um arquivo não seja removido da cache por conta da requisição de um cliente, enquanto outro está recuperando os seus dados. Quando esse arquivo é consultado, a indicação do 'lock' fica com valor True, ao finalizar a consulta retorna para o valor 'False'. o momento em que o servidor buscar liberar espaço na memória, antes de remover um arquivo é verificado o valor do 'lock', remoção somente quando lê o valor 'False'.

Todavia, existe um bloqueio de acesso a cache quando for neessário:
- Consultar um arquivo;
- Remover um arquivo;
- Adicionar um arquivo;

Esse procedimento é realizado a partir da exlusão mútua promovida pela própria biblioteca de Threads do Python. O código a seguir expressa sua utilização:

```python
# to ensure mutual exclusion of cache access
lock = threading.Lock()

# activate the lock
lock.acquire()

# code {}

# disable the lock
lock.release()
```

Basicamente, o código responsável por realizar as operações de alteração ou acesso a cache, estão situados entre bloqueio ou liberação.

<div style="text-align:center"><img src="/assets/cache.png" /></div>

#### <a id="file" />File Acess

O acesso aos arquivos do diretório é feito pelo servior a medida que o cliente faz uma requisição. Dessa maneira, quando um arquivo é solicitado o servidor faz o processo de serialização e como pode haver a consulta por múltiplos clientes, no momento em que um arquivo é aberto para ser serializado, ele é bloqueado e só liberado para uma outra serialização após ser finalizado. Esse processo de serialização também ocorre quando um arquivo é armazenado na cache.

Quando um arquivo não é alocado na memória cache, seu envio é feito apenas por meio de sua serialização toda vez que é requisitado. Então, esse processo de bloqueio é realizado pois se um cliente requisitar um arquivo que já está sendo serializado, a thread responsável por esse novo cliente aguarde a liberação do mesmo.

#### <a id="results" />Results

Os testes realizados foram com base dois clientes simultâneos. A tabela abaixo exibe a sequência de solicitações realizadas por cada cliente:

| Client 1 | Client 2 |
| ------ | ------ |
| python3 tcp_client.py localhost 3000 file5.txt client1/ | python3 tcp_client.py localhost 3000 file5.txt client2/ |
| python3 tcp_client.py localhost 3000 file4.txt client1/ | python3 tcp_client.py localhost 3000 file4.txt client2/ 
| python3 tcp_client.py localhost 3000 list | python3 tcp_client.py localhost 3000 list |
| python3 tcp_client.py localhost 3000 file1.txt client1/ | python3 tcp_client.py localhost 3000 file1.txt client2/ |
| python3 tcp_client.py localhost 3000 file5.txt client1/ | python3 tcp_client.py localhost 3000 file5.txt client2/ |
| python3 tcp_client.py localhost 3000 list | python3 tcp_client.py localhost 3000 list |
| python3 tcp_client.py localhost 3000 file4.txt client1/ | python3 tcp_client.py localhost 3000 file4.txt client2/ |
| python3 tcp_client.py localhost 3000 file2.txt client1/ | python3 tcp_client.py localhost 3000 file2.txt client2/ |
| python3 tcp_client.py localhost 3000 list | python3 tcp_client.py localhost 3000 list |
| python3 tcp_client.py localhost 3000 file3.txt client1/ | python3 tcp_client.py localhost 3000 file3.txt client2/ |
| python3 tcp_client.py localhost 3000 file5.txt client1/ | python3 tcp_client.py localhost 3000 file5.txt client2/ |
| python3 tcp_client.py localhost 3000 list | python3 tcp_client.py localhost 3000 list |
| python3 tcp_client.py localhost 3000 file6.txt client1/ | python3 tcp_client.py localhost 3000 file6.txt client2/ |
| python3 tcp_client.py localhost 3000 file2.txt client1/ | python3 tcp_client.py localhost 3000 file2.txt client2/ |
| python3 tcp_client.py localhost 3000 list | python3 tcp_client.py localhost 3000 list |
| python3 tcp_client.py localhost 3000 file4.txt client1/ | python3 tcp_client.py localhost 3000 file4.txt client2/ |
| python3 tcp_client.py localhost 3000 file5.txt client1/ | python3 tcp_client.py localhost 3000 file5.txt client2/ |
| python3 tcp_client.py localhost 3000 list | python3 tcp_client.py localhost 3000 list |
| python3 tcp_client.py localhost 3000 file4.txt client1/ | python3 tcp_client.py localhost 3000 file4.txt client2/ |
| python3 tcp_client.py localhost 3000 file5.txt client1/ | python3 tcp_client.py localhost 3000 file5.txt client2/ |
| python3 tcp_client.py localhost 3000 list | python3 tcp_client.py localhost 3000 list |
| python3 tcp_client.py localhost 3000 file4.txt client1/ | python3 tcp_client.py localhost 3000 file4.txt client2/ |
| python3 tcp_client.py localhost 3000 file1.txt client1/ | python3 tcp_client.py localhost 3000 file1.txt client2/ |
| python3 tcp_client.py localhost 3000 file2.txt client1/ | python3 tcp_client.py localhost 3000 file2.txt client2/ |
| python3 tcp_client.py localhost 3000 list | python3 tcp_client.py localhost 3000 list |

Os arquivos requisitados e seu respectivo tamanho, são:

| File | Size |
| ------ | ------ |
| File1.txt | 5,2 Mb |
| File2.txt | 10,5 Mb |
| File3.txt | 15,7 Mb |
| File4.txt | 21 Mb |
| File5.txt | 52,4 Mb |
| File6.txt | 68 Mb |

Cada requisição gera mensgens no servidor que são exibidas conforme as operações executadas. A figura animada abaixo exibe o resultados das requisições, onde o terminal maior (esquerda) mostra a execução do servidor e os dois terminais menores (direita) exibem as conexões dos clientes e o retorno recebido:

<div style="text-align:center"><img src="/assets/results_one_server_two_clients.gif" /></div>

***
[MIT License](https://choosealicense.com/licenses/mit/)


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)


   [dill]: <https://github.com/joemccann/dillinger>
   [git-repo-url]: <https://github.com/joemccann/dillinger.git>
   [john gruber]: <http://daringfireball.net>
   [df1]: <http://daringfireball.net/projects/markdown/>
   [markdown-it]: <https://github.com/markdown-it/markdown-it>
   [Ace Editor]: <http://ace.ajax.org>
   [node.js]: <http://nodejs.org>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [jQuery]: <http://jquery.com>
   [@tjholowaychuk]: <http://twitter.com/tjholowaychuk>
   [express]: <http://expressjs.com>
   [AngularJS]: <http://angularjs.org>
   [Gulp]: <http://gulpjs.com>

   [PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>
   [PlGh]: <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>
   [PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>
   [PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>
   [PlMe]: <https://github.com/joemccann/dillinger/tree/master/plugins/medium/README.md>
   [PlGa]: <https://github.com/RahulHP/dillinger/blob/master/plugins/googleanalytics/README.md>
