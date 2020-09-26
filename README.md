# A Multithreaded TCP Server-Client Implementation
###### With cache memory

***

> Higor Santos de Jesus <br>
> Bachelor of Exact and Technological Sciences - UFRB <br>
> Graduating in Computer Engineering - UFRB <br>

- [Overview](#overview)
- [Server](#server)
- [Client](#client)
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

<div style="text-align:center"><img src="/assets/cache.png" /></div>

#### <a id="file" />File Acess

#### <a id="results" />Results

<div style="text-align:center"><img src="/results_one_server_two_clients.gif" /></div>

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
