import os
import subprocess
import random

# veriicar se aquivo existe em diretório
def isExist_file(file_path):
    return os.path.isfile(file_path)

# retorna tamanho do arquivo em MB
def getFile_size(file_path):
    return os.path.getsize(file_path)/(1024 * 1024)

# retorna um dicionário com o nome e tamanho dos arquivos existentes
def list_files_dir(dir_files):
    files = dict()

    os.environ['HOME']
    files = os.listdir(dir_files)

    # list_path_files_with_size = ''

    for f in files:
        f_path = os.path.join(dir_files, f)
        f_size = os.path.getsize(f_path)
        # list_path_files_with_size += f_path.replace(dir_files, '') + '\t' + str(f_size/(1024 * 1024)) + ' MB\n'


        files[f_path.replace(dir_files, '')] = float(f_size/(1024 * 1024))

    # return list_path_files_with_size
    return files