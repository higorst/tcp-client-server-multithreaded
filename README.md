# A Multithreaded TCP Server-Client Implementation
[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)

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
- [Dependencies](#dependecies)

***
#### <a id="overview" />Overview

This project describes the implementation of a TCP client, which retrieves files from a given directory when establishing a connection with a TCP server, as well as obtaining a list of files stored in the cache memory of the same. The cache memory of the server has a maximum limit of 64 MB, as well as the packet transfer buffer a limit of 1024 bytes. After establishing a connection with the server, the client sends a request with the name of the file it wants to retrieve or method of listing the files. The server in turn corresponds to the client's request according to the method invoked. When the file list is requested, the list of files stored in the cache is returned. When a file is requested, the following steps are performed:

- Checks the existence of the file in the directory from which the server is directed;
- Checks whether the file is present in the cache memory;
     - If the file is not in the cache, the server will try to allocate that file:
         - The available space for allocating a new file will be checked;
         - Files will be removed from memory to free up space, when necessary;
         - The file will be serialized in packets, according to the size of the transition buffer;
     - If the file is present, it is sent to the applicant;
     - If the file is larger than the maximum cache limit (64MB), it is not allocated to memory;
- Send the file when available;

***
#### <a id="server" />Server

The TCP server requires a standard in its execution, according to the following parameters:
```sh
$ python3 tcp_server.py host port directory_to_access
```
Being defined by the user:
- __host:__ the connection ip address, which will be accessed by the client.
    - _ex:_ localhost or 127.0.0.1
- __port:__ the connection port, which will be accessed by the customer.
    - _ex:_ 3000 
- __directory_to_access:__ directory from which the files will be accessed.
    - _._ or _./_ for local directory
    - _ex:_ docs/images/  

***
#### <a id="client" />Client

The TCP client requires a standard in its execution depending on the user's needs, according to the following parameter variations:
```sh
$ python3 tcp_client.py host port file_name directory_to_save
or
$ python3 tcp_client.py host port list
```
Being defined by the user:
- __host:__ the connection ip address, must be the same as defined in the tcp_server.
    - _ex:_ localhost or 127.0.0.1
- __port:__ the connection port, must be the same defined in tcp_server.
    - _ex:_ 3000 
- __file_name:__ file you want to retrieve from the server.
    - _ex:_ movie.mp4, market_list.docx 
- __directory_to_save:__ directory from which the files will be accessed.
    - _._ or _./_ for local directory
    - _ex:_ files/receives/documents/  
- __list:__ this nomenclature should be maintained. It serves to request the list of files present in the cache memory of the server.

***
#### <a id="packages" />Package Sending and Receiving

The file recovery process is basically done by sending packages from the server to the client. On the server when a file is accessed it is serialized in packet format, according to the size of the send buffer. These packages, as they are received by the customer, are joined to form the file in the directory chosen by the user.

The code below shows the steps and serialization and deserialization, from reading and writing the file.

```python
# server serializes the data and sends the packets
with open(dir + res2, OPEN_FILE_SERVER) as f:
  package = f.read(BUFFER_SIZE)
  while package:
      # sending file packages
      c.send(package)
      package = f.read(BUFFER_SIZE)
  f.close()

# client receives the packages that make up the file
with open(receive_f, OPEN_FILE_CLIENT) as f:
  package = s.recv(BUFFER_SIZE)
  while package:
      f.write(package)
      package = s.recv(BUFFER_SIZE)
  f.close()
```

***
#### <a id="multithread" />Multi-Thread Implementation

O servidor TCP permite a conexão de mais um cliente por vez, ou seja, diferentes clientes que estabeleçam conexão com o servidor podem solicitar arquivos ou a lista dos presentes na memória cache. Uma abstração desta topologia de conexão pode ser vista na figura abaixo:

<div style="text-align:center"><img src="/assets/server_client_tcp.png" /></div>

This operation comes down to the way in which the server waits for new connections. The communication channel between server and client, called socket, is waiting for a new connection and when it is established, the server allocates it as a thread and is waiting for others. This makes it possible for multiple clients to request files from the server without having to wait for another connection to end.

The code below exemplifies this procedure:
```python
while True:
  # establish connection with client
  c, addr = s.accept()
  # a new thread client
  start_new_thread(threaded, (c, addr, dir))
```

***
#### <a id="cache" />Cache Implementation

The cache memory is built from a hash table structure, the Python dictionary, which has a key and associated content for each position. Its construction on the TCP server is based on the following way:

- The key defined by the file name;
- The content of the key, consisting of three pieces of information:
   - file_size: the file size;
   - file_packages: serialization of the file by sending packets, according to the size of the socket buffer;
   - lock: a flag that identifies whether the file is being consulted by a client or not.

When a file is added to the cache memory, the server associates it in the manner mentioned above. It is worth highlighting the importance of 'lock' content, responsible for ensuring that a file is not removed from the cache due to a client's request, while another is recovering its data. When this file is consulted, the indication of the 'lock' is set to True, when the query ends, it returns to the value 'False'. The moment when the server tries to free space in memory, before removing a file, the value of 'lock' is checked, removal only when it reads the value 'False'.

However, there is a cache access block when it is necessary:
- Consult a file;
- Remove a file;
- Add a file;

This procedure is performed based on the mutual exclusion promoted by the Python Thread library itself. The following code expresses its use:

```python
# to ensure mutual exclusion of cache access
lock = threading.Lock()

# activate the lock
lock.acquire()

'''
code ..
'''

# disable the lock
lock.release()
```

Basically, the code responsible for performing the operations of altering or accessing the cache, are located between blocking or releasing.

<div style="text-align:center"><img src="/assets/cache.png" /></div>

***
#### <a id="file" />File Acess

Access to the files in the directory is done by the server as the client makes a request. In this way, when a file is requested, the server performs the serialization process and as there can be a query by multiple clients, the moment a file is opened to be serialized, it is blocked and only released for another serialization after being finalized. This serialization process also occurs when a file is cached.

When a file is not allocated in the memory cache, it is sent only through serialization whenever it is requested.

So, this blocking process is performed because if a client requests a file that is already being serialized, a thread responsible for this new client waits for its release.o.

The line of code below represents the blocking of the file, while a block of code is executed:

```python
# lock file
with FileLock(path_file + '.lock'):
  # code
  pass
```

***
#### <a id="results" />Results

The tests performed were based on two simultaneous customers. The table below shows the sequence of requests made by each customer:

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

The requested files and their respective size are:

| File | Size |
| ------ | ------ |
| File1.txt | 5,2 Mb |
| File2.txt | 10,5 Mb |
| File3.txt | 15,7 Mb |
| File4.txt | 21 Mb |
| File5.txt | 52,4 Mb |
| File6.txt | 68 Mb |

Each request generates messages on the server that are displayed according to the operations performed.

The animated figure below shows the results of the requests, where the larger terminal (left) shows the server execution and the two smaller terminals (right) show the client connections and the received feedback:

<div style="text-align:center"><img src="/assets/results_one_server_two_clients.gif" /></div>

***
#### <a id="dependecies" />Dependencies

It is necessary to install some dependencies for the operation of this project.

Python 3.6:
```sh
$ sudo apt-get update
$ sudo apt-get install python3.6
```

py-filelock:
```sh
pip3 install filelock
```

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
