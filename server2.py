#!/usr/bin/env python3

import socket
import threading
import argparse
import logging
import sys

logger = logging.getLogger(__name__)
connections = []
handles = {}

def handle_user_connection(connection, address):
    # connection.send("Please enter a username: ".encode())
    username = connection.recv(2048).decode().strip()
    handles[connection] = username

    print(username + " (" + address[0] + ") has joined")

    while True:
        try:
            # Get client message
            msg = connection.recv(2048)

            if msg:
                # Log message sent by user
                print(f'{username}@{address[0]}: {msg.decode()}')
                
                # Build message format and broadcast to users connected on server
                msg_to_send = f'\n{username}: {msg.decode()}'
                broadcast(msg_to_send, connection)

            # Close connection if no message was sent
            else:
                remove(connection)
                break

        except Exception as e:
            print(f'Error handling user connection: {e}')
            remove(connection)
            break

def broadcast(message, connection):
    for client_conn in connections:
        if client_conn != connection:
            try:
                client_conn.send(message.encode())

            # Client disconnected
            except Exception as e:
                print('Error broadcasting message: {e}')
                remove(client_conn)


def remove(conn):
    if conn in connections:
        # Close socket connection and remove connection
        conn.close()
        connections.remove(conn)


def server():
    try:
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((host, port))
        lsock.listen()

        print("listening on", (host, port))
        
        while True:
            # Accept client connection
            socket_connection, address = lsock.accept()
            # Add client connection to connections list
            connections.append(socket_connection)
           
            # Start new client thread
            threading.Thread(target=handle_user_connection, args=[socket_connection, address,]).start()
            print("client " + str(address[0]) + " has joined")

    except Exception as e:
        print(f'An error has occurred when instancing socket: {e}')
    finally:
        # In case of any problem clean all connections and close the server connection
        if len(connections) > 0:
            for conn in connections:
                remove(conn)

        lsock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--server", help="specify server host")
    parser.add_argument("-p", "--port", help="specify bind port to server")
    parser.add_argument("--log", help="enable debug with --log TRUE")
    args = parser.parse_args()

    if not args.server or not args.port:
        print("usage: server.py -i SERVER -p HOST")
        sys.exit(1)
    
    if args.log:
        if args.log.upper() == "TRUE":
            logging.basicConfig(level=logging.DEBUG)

    host, port = args.server, int(args.port)
    server()