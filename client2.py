#!/usr/bin/env python3

import socket
import threading
import argparse
import logging
import sys

def handle_messages(connection):
    while True:
        try:
            msg = connection.recv(2048)

            if msg:
                print(msg.decode())
            else:
                connection.close()
                break

        except Exception as e:
            print(f'Error handling message from server: {e}')
            connection.close()
            break


def client(host, port, username):
    room = "default"

    try:
        # Instantiate socket and start connection with server
        socket_instance = socket.socket()
        socket_instance.connect((host, port))

        socket_instance.send(username.encode())
        socket_instance.send(room.encode())

        # Create a thread in order to handle messages sent by server
        threading.Thread(target=handle_messages, args=[socket_instance]).start()

        print("Connected to "+host)

        # Main event loop
        while True:
            msg = input(username + ": ")

            if msg == 'exit':
                print("Goodbye")
                break

            # Parse message to utf-8
            socket_instance.send(msg.encode())

        # Close connection
        socket_instance.close()

    except Exception as e:
        print(f'Error connecting to server socket {e}')
        socket_instance.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--server", help="specify server host")
    parser.add_argument("-p", "--port", help="specify bind port to server")
    parser.add_argument("-u", "--username", help="specify username")
    parser.add_argument("--log", help="enable debug with --log TRUE")
    args = parser.parse_args()

    if not args.server or not args.port:
        logging.info("usage: client.py -i SERVER -p HOST")
        sys.exit(1)
    
    if args.log:
        if args.log.upper() == "TRUE":
            logging.basicConfig(level=logging.DEBUG)

    while not args.username or args.username == "":
        args.username = input("Specify a username for this session: ")

    host, port, username = args.server, int(args.port), args.username
    client(host, port, username)