# MultiRoom Chat
This is a "game" where there are multiple chatrooms.  Users may freely move between chatrooms. 

See the SOW file for an idea of implementation

There are no third party libraries needed for this project, it can be run natively on the CS machines

To start the chatroom:
1. To start the server: python3 server.py -p PORT
2. To start the client: python3 client.py -i SERVER -p PORT
3. From the client, enter the desired username
4. Now you can chat
5. Use '/exit' from the client to leave the session

Other options:
1. To see the full list of options, use the runtime /help option
2. Enable debug mode by passing --log true as a command line argument
3. To set username when joining, pass -u USERNAME

## Options
### /help
The following options are available:
```
/help - Show available commands
/exit - End the session
/info - Show current room
/list - List available rooms
/join <room> - Join a different room
/add <room> - Create a room
/remove <room> - Delete room
```

## Protocol
The client/server protocol is made up of the following:
* text converted to UTF8 bytes array

## Known Issues
* Thread issues of console output on the client side, shouldn't impact functionality

## Improvements
* Ability to see what users are in current room
* Encryption between client and server
* Permissions of users delegated to create/remove rooms
* Some sort of GUI interface

## Retrospective
For a while, the base code from a programming assignment used was complicated and difficult to maintain.  Moving to a more simple implementation allowed functionality to be built upon it.  The improvement section above gives a good idea of what features would be implemented next.  Overall, I wish I realized to use a simpler code base sooner instead of figuring out the old one, as most of the time spent was troubleshooting rather than adding features.  

I have a refined understanding of how the basics work in python to add the layers of complexity found in the original code base to the current code.