import socket
import sys
import pickle

BUFFER_SIZE = 1024
METHOD_LIST_FILES = 'list'
OPEN_FILE_CLIENT = 'wb'

# vamos criar um socket
s = socket.socket()

host = 'localhost'
port = 3000
res2 = METHOD_LIST_FILES
dir_save = 'receives/'

if len(sys.argv) == 4:
    host = sys.argv[1]          # host
    port = int(sys.argv[2])     # port
    res2 = sys.argv[3]          # method
else:
    host = sys.argv[1]          # host
    port = int(sys.argv[2])     # port
    res2 = sys.argv[3]          # file
    dir_save = sys.argv[4]      # path to save file
    if dir_save[len(dir_save) - 1] != '/': dir_save += '/'
    dir_save = '' if dir_save == '.' else dir_save
    dir_save = '' if dir_save == './' else dir_save

# vamos conectar o socket ao par (endereço, porta)
s.connect((host, port))

res = '1' if res2 == METHOD_LIST_FILES else '2'
msg = pickle.dumps((res, res2))
# vamos enviar os dados
s.sendall(msg)

if res2 == METHOD_LIST_FILES:

    data = s.recv(BUFFER_SIZE)
    while data:
        res = pickle.loads(data)
        print(res)
        data = s.recv(BUFFER_SIZE)

else:
    recived_f = dir_save + res2
    package = s.recv(BUFFER_SIZE)
    res = pickle.loads(package)
    if res:
        with open(recived_f, OPEN_FILE_CLIENT) as f:
            print('downloading', res2)
            package = s.recv(BUFFER_SIZE)
            while package:
                f.write(package)
                package = s.recv(BUFFER_SIZE)
            f.close()
        print("file '%s' saved!" % (res2))
    else:
        print("file '%s' not found on server!" % (res2))
