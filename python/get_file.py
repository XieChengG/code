import paramiko
import time
import os
from stat import S_ISDIR

host = '10.0.0.252'
port = 22
username = 'XCG'
password = '12345678'

transport = paramiko.Transport((host, port))
transport.connect(username=username, password=password)
sftp = paramiko.SFTPClient.from_transport(transport)

x = time.localtime()
date = time.strftime('%Y-%m-%d', x)

remote_path = r"C:\Program Files\PostgreSQL\15\backup\%s" % date
local_path = r"D:\data_backup\postgresql\%s" % date

os.mkdir(local_path)


def sftp_get(remotepath):
    path = remotepath
    folders = []
    files = []
    for f in sftp.listdir_attr(remotepath):
        if S_ISDIR(f.st_mode):
            folders.append(f.filename)
        else:
            files.append(f.filename)
    if files:
        yield path, files
    for folder in folders:
        new_path = os.path.join(remotepath, folder)
        for x in sftp_get(new_path):
            yield x


for path, files in sftp_get(remote_path):
    for file in files:
        sftp.get(path + '/' + file, os.path.join(local_path, file))
