#!/usr/bin/env python3

import socket
import threading
import argparse
import logging
import sys
import time

exit_signal = threading.Event()

def handle_messages(connection):
    while not exit_signal.is_set():
        try:
            msg = connection.recv(2048)

            if msg:
                sys.stdout.write("\r" + " " * 80)
                sys.stdout.write("\r" + msg.decode())
                sys.stdout.flush()
                sys.stdout.write(f"\n{username}: ")
                sys.stdout.flush()
            else:
                print("\nServer disconnected, exiting")
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
        time.sleep(0.1)
        socket_instance.send(room.encode())

        # Create a thread in order to handle messages sent by server
        listen_thread = threading.Thread(target=handle_messages, args=[socket_instance])
        listen_thread.start()

        print("\rConnected to " + host + "\n")
        print("Use the /help command for a description of options")

        # Main event loop
        while not exit_signal.is_set():
            msg = input(username + ": ")

            if msg == '/exit':
                exit_signal.set() # stop the thread
                socket_instance.send(msg.encode())
                socket_instance.close()
                break

            # Parse message to utf-8
            socket_instance.send(msg.encode())

    except Exception as e:
        print(f'Error connecting to server socket, is the server up?')
    finally:
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