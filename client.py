#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback

import libclient

sel = selectors.DefaultSelector()

handle = None
handle_2 = None

def create_request(action, value):
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

def start_connection(host, port, request):
    addr = (host, port)
    print("starting connection to", addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)

if len(sys.argv) != 3:
    print("usage:", sys.argv[0], "<host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
# action, value = sys.argv[3], sys.argv[4]

if handle is None: # the username hasn't been set
    handle = input("Please set a username: ")

request = create_request("register", handle) # register username

print("Send 'join' to go to a chatroom. Use 'exit' at any time to quit")
if handle_2 is None:
    handle_2 = input("'join' or 'exit'")
if handle_2 == 'join':
    start_connection(host, port, request)
    print("Use 'exit' at any time to quit")
#if handle_2 == 'exit':
#    handle = 'exit'

try:
    while True:
        events = sel.select(timeout=1)
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
            request = create_request("message", msg)
            # Send new messages without reconnecting
            message._send_buffer += message._create_message(
                content_bytes=message._json_encode(request['content'], 'utf-8'),
                content_type=request['type'],
                content_encoding=request['encoding']
            )

except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()