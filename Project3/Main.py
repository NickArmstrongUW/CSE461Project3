#!/usr/bin/env python

import threading
import sys
import socket
from random import randint
from datetime import datetime

DEFAULT_PORT = 1234

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
    sock.bind(("0.0.0.0", port))
    fprint("Proxy listening on 0.0.0.0:%d" % (port))

    while True:
        sock.listen(1)
        try:
            connection, address = sock.accept() # not able to handle multiple clients
            thread = threading.Thread(target=run, args=[connection, address])
            thread.start()
        except socket.timeout: 
            pass # or continue
            # socket.close()
            # sys.exit()
    sock.close()

def run(connection, address):
    # connection is client socket
    print("entered run")
    try:

        # connection is probably a socket to the client just use that
        # IF CONNECTION IS NOT A SOCKET use connection and addr to get a sock for client
        # to read in header
            # some sort obj that you keep adding bytes to as they come in
            # loop terminate cond \r\n\r\n

        # after reading in header, next data in socket is payload
        # setup a socket obj that connects to the server
        # find if it is connect or not
            # if not connect
                # filter out keep alive (turn to close)
                # fwd header, payload to server
                # fwd server resp to client
            # if is connect
                # send back that HTTP ok to client
                # create 2 thds:
                    # 1 thd forwards all traffic server to client
                    # 1 thd forwards all traffic client to server
                # typically these two thds finish running with a crazy amount of exceptions since one of the connection was closed
        # close the sockets

        #what is client?
        
        # read in the header
        header = connection.recv(1)
        while '\r\n\r\n' not in str(header):
            header += connection.recv(1)

        headers = header.split('\r\n')
        fprint(headers[0])
        fields = headers[0].split()

        # set up socket obj that connects to server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # getting host
        HOST = socket.gethostbyname(str(fields[1]))
        print("Host is ", HOST)
        server.connect((HOST, 80))
        print("server has connected")

        if fields[0] is 'CONNECT':
            handle_connection(connection, address, server, HOST)
        else:
            handle_nonconnection(connection, address, header, server, HOST)
        
    except Exception as e:
        print("exception ", e)
        return
    
    server.close()
    

# send back that HTTP ok to client
# create 2 thds:
    # 1 thd forwards all traffic server to client
    # 1 thd forwards all traffic client to server
# typically these two thds finish running with a crazy amount of exceptions since one of the connection was closed
def handle_connection(connection, address, server, server_ip):
    print("handling connection")
    # send back that HTTP ok to client
    try:
        message = "HTTP/1.0 200 OK \r\n\r\n" # double carriage return
        connection.sendto(message)
    except Exception:
        message = "HTTP/1.0 502 Bad Gateway \r\n\r\n" # double carriage return
        connection.sendto(message)
        server.close()
        return
    
    # create 2 thds:
        # 1 thd forwards all traffic server to client
        # 1 thd forwards all traffic client to server
         # typically these two thds finish running with a crazy amount of exceptions since one of the connection was closed
    try:
        client2serv = thread.Thread(target=forward_information, args=[connection, server,  (server_ip, 80)])
        forward_information(server, connection, address)
    except Exception:
        server.close()
        return


def forward_information(input, output, address):
    while True:
        d_in = input.recv(1024)
        output.sendto(d_in, address)

# filter out keep alive (turn to close)
# fwd header, payload to server
        # fwd server resp to client
def handle_nonconnection(connection, address, header, server, server_ip):
    print("handling nonconnection")
    # filter out keep alive (turn to close)
    split_header = header.split(delimeter='\r\n')
    keep_alive = header.find('keep-alive')
    new_request = ""
    if keep_alive == -1:
        # keep alive is not in it, so new request is the same
        new_request = header
    else:
        # replace keep-alive with close
        new_request = header[0: keep_alive] + 'close' + header[keep_alive + 10:]

    # fwd header, payload to server
    # fwd server resp to client
    server.sendto(header, (server_ip, 80))
    server.sendto(new_request, (server_ip, 80))
    data = server.recv(1024)
    connection.sendto(data, address)


if __name__ == '__main__':
    main()