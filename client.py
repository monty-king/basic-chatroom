#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback

import libclient

handle = None
handle_2 = None

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.addr = (host, port)
        self.sel = selectors.DefaultSelector()

    def send_request(self, sock, request):
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        message = libclient.Message(self.sel, sock, self.addr, request)
        self.sel.register(sock, events, data=message)

    def start_connection(self):
        print("starting connection to", self.addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(self.addr)

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
    if len(sys.argv) != 3:
        print("usage:", sys.argv[0], "<host> <port>")
        sys.exit(1)

    host, port = sys.argv[1], int(sys.argv[2])

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
                # Send new messages without reconnecting
                message._send_buffer += message._create_message(
                    content_bytes=message._json_encode(request['content'], 'utf-8'),
                    content_type=request['type'],
                    content_encoding=request['encoding']
                )
                client.send_request(socket_connection, request)

    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    finally:
        client.sel.close()