#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import argparse

import libclient

handle = None
handle_2 = None

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.addr = (host, port)
        self.sel = selectors.DefaultSelector()
        self.messages = None

    def send_request(self, sock, request):
        if self.messages:
            self.messages._send_buffer += self.messages._create_message(
                content_bytes=self.messages._json_encode(request['content'], 'utf-8'),
                content_type=request['type'],
                content_encoding=request['encoding']
            )
        else:
            print("No messages instance found")

    def start_connection(self):
        print("starting connection to", self.addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(self.addr)

        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.messages = libclient.Message(self.sel, sock, self.addr, request)
        self.sel.register(sock, events, data=self.messages)

        return sock

    def create_request(self, action, value):
        if action in ["register", "message"]:
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, value=value),
            )
        else:
            return dict(
                type="binary/custom-client-binary-type",
                encoding="binary",
                content=bytes(action + value, encoding="utf-8"),
            )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--server", help="specify server host")
    parser.add_argument("-p", "--port", help="specify bind port to server")
    args = parser.parse_args()

    if not args.server or not args.port:
        print("usage: server.py -i SERVER -p HOST")
        sys.exit(1)

    host, port = args.server, int(args.port)

    if handle is None: # the username hasn't been set
        handle = input("Please set a username: ")

    client = Client(host, port)
    print(f"Welcome, {handle}")

    request = client.create_request("register", handle) # register username
    socket_connection = client.start_connection()
    client.send_request(socket_connection, request)

    # print("Send 'join' to go to a chatroom. Use 'exit' at any time to quit")
    # if handle_2 is None:
    #     handle_2 = input("'join' or 'exit'")
    # if handle_2 == 'join':
        
    #     print("Use 'exit' at any time to quit")
    # #if handle_2 == 'exit':
    # #    handle = 'exit'

    try:
        while True:
            events = client.sel.select(timeout=1)
            for key, mask in events:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print(
                        "main: error: exception for",
                        f"{message.addr}:\n{traceback.format_exc()}",
                    )
                    message.close()

            if handle:
                msg = input(f"{handle}: ")
                if msg.lower() == "exit":
                    break
                request = client.create_request("message", msg)
                client.send_request(socket_connection, request)
                print("Sending message: "+msg)
                # Send new messages without reconnecting
                
                # client.send_request(socket_connection, request)

    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    finally:
        client.sel.close()