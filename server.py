#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import argparse
import logging

import libserver

sel = selectors.DefaultSelector()
clients = {}
logger = logging.getLogger(__name__)

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def run(self):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((host, self.port))
        lsock.listen()
        print("listening on", (host, self.port))
        lsock.setblocking(False)
        sel.register(lsock, selectors.EVENT_READ, data=None)

        try:
            while True:
                events = sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        Server.accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                        except Exception:
                            logging.info(
                                "main: error: exception for",
                                f"{message.addr}:\n{traceback.format_exc()}",
                            )
                            message.close()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            sel.close()

    def accept_wrapper(sock):
        conn, addr = sock.accept()  # Should be ready to read
        logging.info("accepted connection from "+str(addr))
        conn.setblocking(False)
        message = libserver.Message(sel, conn, addr)
        sel.register(conn, selectors.EVENT_READ, data=message)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="specify listening port for server")
    parser.add_argument("--log", help="enable debug with --log TRUE")
    args = parser.parse_args()

    if args.log:
        if args.log.upper() == "TRUE":
            logging.basicConfig(level=logging.DEBUG)
    
    host, port = "0.0.0.0", int(args.port)
    s = Server(host, port)
    s.run()
    