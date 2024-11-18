import sys
import selectors
import json
import io
import struct
import logging

clients = {}
logger = logging.getLogger(__name__)

class Message:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.username = None
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False
        self.clients = []

    def _set_selector_events_mask(self, mode):
        print("set mask")
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        print("_read")
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        print("_write")
        if self._send_buffer:
            logging.info("sending" + repr(self._send_buffer) + " to " + str(self.addr))
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                #if sent and not self._send_buffer:
                #    self._set_selector_events_mask("r")
                #     self.close()

    def _json_encode(self, obj, encoding):
        print("json encode")
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        print("json decode")
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        print("create message")
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message
    
    def broadcast_message(self, message):
        print("broadcast message")
        for username, client in clients.items():
            if client != self:
                client.queue_message(message)

    def queue_message(self, message):
        print("queue message")
        content = {"result": f"{self.username}: {message}"}
        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        self._send_buffer += response["content_bytes"]

    def _create_response_json_content(self):
        print("create json response")
        global clients

        action = self.request.get("action")
        if action == "register":
            username = self.request.get("value")

            if username:
                if username in clients:
                    content = {"result": f"Error: username already taken!  Please choose a different one."}
                else:
                    self.username = username
                    clients[username] = self
                    print(f"User '{username}' registered from {self.addr}")
                    content = {"result": f"Username '{username}' registerd successfully "}
            else:
                content = {"result": f"Error: null username registerd from {self.addr}"}
       
        elif action == "message":
            message = self.request.get("value")
            logging.info(f"Received message: {message}")
            content = {"result": f"Message received: {message}"}

            self.broadcast_message(message)
        else:
            content = {"result": f'Error: invalid action "{action}".'}
        
        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response

    #def _create_response_binary_content(self):
    #    print("create binary response")
    #    response = {
    #        "content_bytes": b"First 10 bytes of request: "
    #        + self.request[:10],
    #        "content_type": "binary/custom-server-binary-type",
    #        "content_encoding": "binary",
    #    }
    #    return response

    def process_events(self, mask):
        print("process events")
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        print("read")
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.request is None:
                self.process_request()

    def write(self):
        print("write")
        if self.request:
            if not self.response_created:
                self.create_response()

        self._write()

        # after writing message, enter read mode to receive new message
        if not self._send_buffer:
            if self.sock:
                self._set_selector_events_mask("r")

    def close(self):
        print("close")
        global clients

        if self.username in clients:
            print(f"Removing user '{self.username}' as they probably disconnected")
            del clients[self.username]

        print("closing connection to", self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            logging.debug(
                f"error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )

        try:
            self.sock.close()
        except OSError as e:
            logging.debug(
                f"error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def process_protoheader(self):
        print("process proto header")
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        print("process json header")
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_request(self):
        print("process request")
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)
            logging.info("received request" + str(repr(self.request)) + " from " + str(self.addr))
        else:
            # Binary or unknown content-type
            self.request = data
            logging.info(
                f'received {self.jsonheader["content-type"]} request from',
                self.addr,
            )
        # Set selector to listen for write events, we're done reading.
        self._set_selector_events_mask("w")

    def create_response(self):
        print("create response")
        if self.jsonheader["content-type"] == "text/json":
            response = self._create_response_json_content()
        else:
            pass
            # Binary or unknown content-type
            #response = self._create_response_binary_content()
        message = self._create_message(**response)
        self.response_created = True
        self._send_buffer += message