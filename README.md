# MultiRoom Chat
This is a "game" where there are multiple chatrooms.  Each room has different functionality where you can do different things.  

See the SOW file for an idea of implementation

There are no third party libraries needed for this project.

To start the chatroom:
1. To start the server: python3 server.py -p PORT
2. To start the client: python3 client.py -i SERVER -p PORT
3. From the client, enter the desired username
4. Now you can chat
5. Use '/exit' from the client to leave the session

Other options:
1. To see the full list of options, use the runtime /help option
2. Enable debug mode by passing --log true as a command line argument

## Options
### /help
The following options are available:
/help - Show available commands
/exit - End the session
/info - Show current room
/list - List available rooms
/join <room> - Join a different room
/add <room> - Create a room
/remove <room> - Delete room


## Protocol
The client/server protocol is made up of the following:
* text converted to UTF8 bytes array