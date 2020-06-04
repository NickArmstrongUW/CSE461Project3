#!/usr/bin/env python

import threading
import sys
import socket
from random import randint
from datetime import datetime
import re

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
    sock.settimeout(10)
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

    print("entered run")
    
    try:
        # read in the header
        header = connection.recv(1)
        while '\r\n\r\n' not in str(header):
            header += connection.recv(1)

        try:
            headers = header.split('\r\n')
        except TypeError:
            print("headers failed at: ", headers)
        fprint(headers[0])
        try:
            fields = headers[0].split()
        except TypeError:
            print("fields failed at: ", headers[0])

        # set up socket obj that connects to server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(10)
        # getting host and port
        url_port = fields[1].split(':')
        port = 80
        if url_port[-1].isdigit(): # port is the last index then
            port = url_port[-1]
            url = ""
            for i in range(0, len(url_port) - 1):
                url += url_port[i] + ":"
            url = url[:-1]
        else: # check if port was given in the Host line and set url
            url = fields[1]
            for line in headers:
                if 'host:' in line.lower():
                    fields = line.split()
                    url_port = fields[1].split(':')
                    if url_port[-1].isdigit(): # port is the last index then
                        port = url_port[-1]
                    break
            if 'https' in url: # still don't find port
                port = 443
        port = int(port)
        print("port is: ", port)
        
        if '//' in url:
            url = url.split('//')[1]
        if url[-1] is '/':
            url = url[:-1]
        print("url is: ", url)
        HOST = socket.gethostbyname(url)
        print("HOST is: ", HOST)
        server.connect((HOST, port))
        print("server has connected", (HOST, port))

        if 'CONNECT' in fields[0]:
            handle_connection(connection, address, server, HOST, port)
        else:
            handle_nonconnection(connection, address, header, server, HOST, port)
        
    except Exception as e:
        print("exception ", e)
        return
    
    server.close()
    

# send back that HTTP ok to client
# create 2 thds:
    # 1 thd forwards all traffic server to client
    # 1 thd forwards all traffic client to server
# typically these two thds finish running with a crazy amount of exceptions since one of the connection was closed
def handle_connection(connection, address, server, server_ip, port):
    print("handling connection")
    # send back that HTTP ok to client
    try:
        message = "HTTP/1.0 200 OK \r\n\r\n" # double carriage return
        connection.sendto(message, address)
    except Exception:
        message = "HTTP/1.0 502 Bad Gateway \r\n\r\n" # double carriage return
        connection.sendto(message, address)
        server.close()
        return
    
    # create 2 thds:
        # 1 thd forwards all traffic server to client
        # 1 thd forwards all traffic client to server
         # typically these two thds finish running with a crazy amount of exceptions since one of the connection was closed
    try:
        client2serv = threading.Thread(target=forward_information, args=[connection, server,  (server_ip, port)])
        client2serv.start()
        forward_information(server, connection, address)
    except Exception:
        server.close()
        return
    
    server.close()
    return

# helper for handle connection
def forward_information(host, client, address):
    host.setblocking(0)
    while True:
        try:
            d_in = host.recv(1024)
        except socket.error as e:
            print("finished connection on recv with error ", e)
            return
        try:
            client.sendall(d_in)
        except socket.error as e:
            print("finished connection on send with error ", e)
            return
        

# filter out keep alive (turn to close)
# fwd header, payload to server
        # fwd server resp to client
def handle_nonconnection(connection, address, header, server, server_ip, port):
    print("handling nonconnection")
    # filter out keep alive (turn to close)
    new_request = process_header(header)
    
    # forward modified header to server
    server.sendall(new_request)
    
    # receive data from server until they stop sending
    server.settimeout(10)
    while True:
        try: 
            data = server.recv(1024)
            if len(data) == 0:
                break
            # proc_response = process_header(data)
            connection.sendall(data)
        except socket.timeout:
            break
    
    # process data from server, then send to client
    

def process_header(header):
    print("original header is", header)
    new_header = header
    new_header = new_header.replace('keep-alive', 'close')
    new_header = new_header.replace('HTTP/1.1', 'HTTP/1.0')
    # new_header
    # headers = header.split('\r\n')
    # fprint(headers[0])
    # new_request = ""
    # for i in range(len(headers)):
    #     headers[i].replace('keep-alive', 'close')
    #     #HTTP/#.#
    #     # headers[i] = headers[i][:headers[i].find('HTTP/')] + 'HTTP/1.0'        
    #     new_request = new_request + headers[i] + '\r\n'

    print("new_request is: ", new_header)
    return new_header


if __name__ == '__main__':
    main()