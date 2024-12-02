#!/usr/bin/env python3

import socket
import threading
import argparse
import logging
import sys

logger = logging.getLogger(__name__)
connections = []
handles = {}
user_rooms = {}
rooms = ["default"]

def handle_user_connection(connection, address):
    username = connection.recv(2048).decode().strip()
    handles[connection] = username
    room = connection.recv(2048).decode().strip()
    if room not in rooms:
        room = "default"

    user_rooms[connection] = room
    connection.send(("\n\nYou are currently in room " + room).encode())

    print(username + " (" + address[0] + ") has joined")
    broadcast(username + " has joined", connection)

    while True:
        try:
            # Get client message
            msg = connection.recv(2048)

            if msg:

                if msg.decode() == "/exit":
                    print(username + " (" + address[0] + ") has left")
                    broadcast(username + " has left the chat", connection)
                    send("\nGoodbye\n", connection)
                    remove(connection)
                    break

                elif msg.decode()[0] == "/":
                    parse_user_command(msg.decode(), connection)

                else:
                    # Broadcast to users connected on server
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

def parse_user_command(command, client_conn):
    username = handles.get(client_conn)
    try:
        cmd = command[1:command.index(" ")]
    except ValueError:
        cmd = command[1:]

    if cmd == "help":
        help_msg = "\n/help - Show available commands\n" \
                   "/exit - End the session\n" \
                   "/info - Show current room\n" \
                   "/list - List available rooms\n" \
                   "/join <room> - Join a different room\n" \
                   "/add <room> - Create a room\n" \
                   "/remove <room> - Delete room\n"
        send(help_msg, client_conn)

    elif cmd == "info":
        current_room = user_rooms.get(client_conn)
        send("\nYou are currently in room: " + current_room + "\n", client_conn)

    elif cmd == "join":
        try:
            target_room = command.split(" ", 1)[1].strip()
            if target_room in rooms:
                broadcast(username + " has left the chat", client_conn)
                current_room = user_rooms.get(client_conn)
                user_rooms[client_conn] = target_room
                send("\nYou have joined room " + target_room + "\n", client_conn)
                broadcast(username + " has joined the chat", client_conn)

            else:
                send("\nThis room does not exist.  Perhaps create it with the /add command?\n", client_conn)

        except IndexError:
            send("\nUsage: /join <room>\n", client_conn)

    elif cmd == "add":
        try:
            target_room = command.split(" ", 1)[1].strip()
            if target_room not in rooms:
                rooms.append(target_room)
                user_rooms[client_conn] = target_room
                send("\nRoom " + target_room + " has been created\n", client_conn)

            else:
                send("\nRoom already exists\n", client_conn)

        except IndexError:
            send("\nUsage: /add <room>\n", client_conn)

    elif cmd == "remove":
        try:
            target_room = command.split(" ", 1)[1].strip()

            if target_room == "default":
                send("\nCannot remove the default room\n", client_conn)

            elif target_room in rooms:
                active_users = [conn for conn, room in user_rooms.items() if room == target_room]
                if active_users:
                    send("\nCannot remove room " + target_room + " because it is occupied\n", client_conn)
                else:
                    rooms.remove(target_room)
                    send("\nRoom " + target_room + " has been deleted\n", client_conn)

            else:
                send("\nRoom doesn't exist\n", client_conn)

        except IndexError:
            send("\nUsage: /remove <room>\n", client_conn)

    elif cmd == "list":
        chatrooms = "\nAvailable Rooms\n===============\n"
        for room in rooms:
            chatrooms += room + "\n"
        
        send(chatrooms, client_conn)

    else:
        send("\nUnknown command, use /help for available options\n", client_conn)


def broadcast(message, connection):
    broadcast_room = user_rooms.get(connection)
    for client_conn in connections:
        if client_conn != connection and user_rooms.get(client_conn) == broadcast_room:
            try:
                client_conn.send(message.encode())

            # Client disconnected
            except Exception as e:
                print('Error broadcasting message: {e}')
                remove(client_conn)

def send(message, connection):
    connection.send(message.encode())


def remove(conn):
    if conn in connections:
        # Close socket connection and remove connection
        username = handles.pop(conn, None)
        room = user_rooms.pop(conn, None)
        conn.close()
        connections.remove(conn)

        broadcast(username + " left the chat", conn)


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
            connections.append(socket_connection)
           
            # Start new client thread
            threading.Thread(target=handle_user_connection, args=[socket_connection, address,]).start()

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
    parser.add_argument("-p", "--port", help="specify bind port to server")
    parser.add_argument("--log", help="enable debug with --log TRUE")
    args = parser.parse_args()

    if not args.port:
        print("usage: server.py -p HOST")
        sys.exit(1)
    
    if args.log:
        if args.log.upper() == "TRUE":
            logging.basicConfig(level=logging.DEBUG)

    host, port = "0.0.0.0", int(args.port)
    server()