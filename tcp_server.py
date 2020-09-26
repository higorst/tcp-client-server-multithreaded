import socket
import sys
import pickle
import random

from time import sleep

from _thread import *
import threading

import os
import subprocess
from filelock import FileLock
import manager_files

CACHE_SIZE = 64
BUFFER_SIZE = 1024
OPEN_FILE_SERVER = 'rb'

'''
    cache memory dictionary 'key' : 'value'

    'file_name' : [file_size, file_packages, lock]
                   file_size = tamanho do arquivo  
                   file_packages = [
                       'package 1', 
                       'package 2', 
                       ..
                   ]   
                   lock = true or false
'''
cache = dict()
cache_available = CACHE_SIZE

# thread function for client instance
def threaded(c, addr, dir):

    # access to global variables
    global cache
    global cache_available
    global lock

    # receives the client's request
    data = c.recv(BUFFER_SIZE)
    # this request is deserialized
    res1, res2 = pickle.loads(data)

    # option 1: view cache files
    if res1 == '1':

        print(
            "|LOG|: ------- [port: %s] checking files on cache for client" % (addr[1]))
        if len(cache) == 0:
            c.send(pickle.dumps('|CACHE| Status: empty'))
        else:
            package = '\n|CACHE| Files:\n\n'
            for file in cache.keys():
                package += file + '\n'
            c.send(pickle.dumps(package))

            print(
                "|LOG|: ------- [port: %s] list files on cache sended to client" % (addr[1]))

    # option 2: download a file
    elif res1 == '2':
        print("|LOG|: ------- [port: %s] client is requesting file '%s'" % (
            addr[1], res2))
        # check if file exists in the directory or cache
        if manager_files.isExist_file(dir + res2) or res2 in cache:
            # checks if file is larger than the cache
            if manager_files.getFile_size(dir + res2) > CACHE_SIZE and res2 not in cache:
                print("|LOG|: ------- [port: %s] sending file '%s' to client" % (
                    addr[1], res2))
                # prepares client to receive file
                package = pickle.dumps(True)
                c.send(package)

                # serialization of the file for sending
                with FileLock(dir + res2 + '.lock'):
                    with open(dir + res2, OPEN_FILE_SERVER) as f:
                        package = f.read(BUFFER_SIZE)
                        while package:
                            # sending file packages
                            c.send(package)
                            package = f.read(BUFFER_SIZE)
                        sleep(1)
                        f.close()

                print("|LOG|: ------- [port: %s] sent file '%s' to client" % (
                    addr[1], res2))
            else:
                # activate the lock
                lock.acquire()
                # check if file exists in cache
                if res2 not in cache:

                    print("|LOG|: |CACHE| [port: %s] add file '%s' on cache" % (
                        addr[1], res2))
                    size_file = manager_files.getFile_size(dir + res2)

                    # free up cache space
                    if cache_available < size_file:
                        for key_file in list(cache):
                            # remove file from cache
                            if not cache[key_file][2]:
                                print("|LOG|: |CACHE| [port: %s] remove a file '%s' by cache" % (
                                    addr[1], key_file))
                                file_removed = cache.pop(key_file)
                                file_removed_size = file_removed[0]
                                cache_available += file_removed_size

                    # serialize file
                    packages = []
                    with FileLock(dir + res2 + '.lock'):
                        with open(dir + res2, OPEN_FILE_SERVER) as f:
                            package = f.read(BUFFER_SIZE)
                            while package:
                                packages.append(package)
                                package = f.read(BUFFER_SIZE)
                            sleep(1)
                            f.close()

                    # add file to cache
                    cache[res2] = [size_file, packages, True]
                    cache_available -= size_file

                    print("|LOG|: |CACHE| [port: %s] file '%s' on cache" % (
                        addr[1], res2))


                # block cache file
                cache[res2][2] = True

                # query cache file to be sent
                file_in_cache = cache[res2]
                size_file = file_in_cache[0]
                packages = file_in_cache[1]

                # flush file from cache
                cache[res2][2] = False
                
                # disable the lock
                lock.release()

                # -------
                # sending through the cache
                print("|LOG|: |CACHE| [port: %s] sending file '%s' to client" % (
                    addr[1], res2))
                package = pickle.dumps(True)
                c.send(package)

                for package in packages:
                    c.send(package)
                sleep(1)
                print("|LOG|: |CACHE| [port: %s] sent file '%s' to client" % (
                    addr[1], res2))
        # if file does not exist
        else:
            print("|LOG|: ------- [port: %s] file '%s' not found" % (
                addr[1], res2))
            # warns that file does not exist
            package = pickle.dumps(False)
            c.send(package)

    print("|LOG|: ------- [port: %s] closed connection with client" % (addr[1]))
    c.close()


# to ensure mutual exclusion of cache access
lock = threading.Lock()

HOST = sys.argv[1]
PORT = int(sys.argv[2])
dir = sys.argv[3]
if dir[len(dir) - 1] != '/': dir += '/'
dir = '' if dir == '.' else dir
dir = '' if dir == './' else dir

# definições do socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
print('\nsocket bind to port: %s' % (PORT))

# put the socket into listening mode
s.listen(5)
print("socket is listening")
print("set: 'ctrl + c' to kill server\n")

try:
    # a forever loop to server
    while True:
        # establish connection with client
        c, addr = s.accept()
        print('|LOG|: ------- [port: %s] new connection with client' % (addr[1]))

        # a new thread client
        start_new_thread(threaded, (c, addr, dir))
except: pass
finally:
    print("|LOG|: SERVER OFF %s:%s" % (HOST,PORT))
    # close connection server
    s.close()
