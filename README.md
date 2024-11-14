# MultiRoom Chat
This is a "game" where there are multiple chatrooms.  Each room has different functionality where you can do different things.  

See the SOW file for an idea of implementation

To start the chatroom:
1. To start the server: python3 server.py \<port\>
2. To start the client: python3 client.py \<server-hostname\> \<port\>
3. From the client, enter the desired username
4. Now you can chat.

## Protocol
The client/server protocol is made up of the following:
* a fixed length 2 byte integer
* a variable length unicode (UTF8) JSON header; length specified by the fixed length header
* a variable length content body; type and length specified by JSON header