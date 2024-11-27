import socket
import threading
import argparse
import logging
import sys

def handle_messages(connection: socket.socket):
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

def client(host, port):
    try:
        # Instantiate socket and start connection with server
        socket_instance = socket.socket()
        socket_instance.connect((host, port))
        # Create a thread in order to handle messages sent by server
        threading.Thread(target=handle_messages, args=[socket_instance]).start()

        print("Connected to "+host)

        # Main event loop
        while True:
            msg = input()

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
    parser.add_argument("--log", help="enable debug with --log TRUE")
    args = parser.parse_args()

    if not args.server or not args.port:
        logging.info("usage: server.py -i SERVER -p HOST")
        sys.exit(1)
    
    if args.log:
        if args.log.upper() == "TRUE":
            logging.basicConfig(level=logging.DEBUG)

    host, port = args.server, int(args.port)
    client(host, port)