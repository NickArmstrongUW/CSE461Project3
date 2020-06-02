#!/usr/bin/env python

import threading
import sys
import socket
from random import randint
from datetime import datetime

DEFAULT_PORT = 80

def fprint(data):
    now = datetime.now()
    print("%s %s %s - " % (now.strftime("%-d"), 
        now.strftime("%b"), now.strftime("%H:%M:%S")), data)

def main():
    # create a connection?
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = DEFAULT_PORT
    
    # setup our socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # ip = socket.gethostbyname("localhost")
    # create socket, bind, listen, accept
    tcp_port = randint(50000, 65535)
    sock.bind(("0.0.0.0", tcp_port))
    fprint("Proxy listening on 0.0.0.0:%d" % (tcp_port))
    

    while True:
        sock.listen(1)
        try:
            connection, address = sock.accept()
            # threading here
            thread = threading.Thread(target=handle_connection, args=[connection, address])
            thread.start()
        except socket.timeout: 
            socket.close()
            sys.exit()
    socket.close()

def run():
    try:
        #what is client?
        result = client.recv(1024)
        data = bytes(result, "utf8")
        fprint(data)
        
        new_port = 80   # because hTTP version?
        http_type = data.find('HTTP/1.1')
        keep_alive = data.find('keep-alive')
        end_of_curr_header = data.find('r\n\r\n')

        new_request = ""
        if keep_alive == -1:
            #keep alive is not in it, so new request is the same
            new_request = data
        else:
            #replace keep-alive with close
            new_request = data[0: keep-alive] + 'close' + data[keep-alive + 10:]
        
    except Exception:
        return

    if request == 'CONNECT':
        handle_connection(connection, address)
    else:
        handle_nonconnection(connection, address)


def handle_connection(connection, address):
    sock2 = socket.socket(sock.AF_INET, socket.SOCK_STREAM)
    message = ""    
    try:
        sock2.connect(connection, address)
        message = "HTTP/1.0 200 OK \r\n"
        connection.sendto(message)
        # send client and send message
    except Exception:
        message = "HTTP/1.0 502 Bad Gateway \r\n"
        # send client and send message
        sock2.close()
        return
    
    sock2.close()

def handle_nonconnection(connection, address):
    sock2 = socket.socket(sock.AF_INET, socket.SOCK_STREAM)
    message = ""    
    try:
        sock2.connect(connection, address)
        message = "HTTP/1.0 200 OK \r\n"
        connection.sendto(message)
        # send client and send message
    except Exception:
        message = "HTTP/1.0 502 Bad Gateway \r\n"
        # send client and send message
        sock2.close()
        return
    
    sock2.close()


if __name__ == '__main__':
    main()