#!/usr/bin/env python3

import socket
import threading
import argparse
import logging
import sys

logger = logging.getLogger(__name__)
connections = []

def handle_user_connection(connection: socket.socket, address: str) -> None:
    while True:
        try:
            # Get client message
            msg = connection.recv(2048)

            if msg:
                # Log message sent by user
                print(f'{address[0]}:{address[1]} - {msg.decode()}')
                
                # Build message format and broadcast to users connected on server
                msg_to_send = f'From {address[0]}:{address[1]} - {msg.decode()}'
                broadcast(msg_to_send, connection)

            # Close connection if no message was sent
            else:
                remove(connection)
                break

        except Exception as e:
            print(f'Error to handle user connection: {e}')
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


def remove(conn: socket.socket) -> None:
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
            threading.Thread(target=handle_user_connection, args=[socket_connection, address]).start()
            print("Client " + str(address) + " has joined")

    except Exception as e:
        print(f'An error has occurred when instancing socket: {e}')
    finally:
        # In case of any problem we clean all connections and close the server connection
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