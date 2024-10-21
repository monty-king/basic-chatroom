# MultiRoom Chat
This is a "game" where there are multiple chatrooms.  Each room has different functionality where you can do different things.  

See the SOW file for an idea of implementation

To start the chatroom:
1. Run 'python3 server.py' to start the server.
2. Run 'python3 client.py <server address> 31337' to connect a client.
3. Enter a username either in the second step or now.
4. Now you can chat.

## Protocol
The client/server protocol is made up of the following:
* a fixed length 2 byte integer
* a variable length unicode (UTF8) JSON header; length specified by the fixed length header
* a variable length content body; type and length specified by JSON header