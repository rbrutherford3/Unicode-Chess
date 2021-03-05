# ASCII-Chess (now with online games)

This program is four Python files to play games of two-player chess using monospace characters and algebraic notation to dictate moves.  All rules of chess are enforced, including check, checkmate, special pawn moves, promotion of pawn after reaching the other side, king-side and queen-side castle, etc.  A game can be played either at the same machine (trading places for each turn) or online between two machines (more below).

![Program Startup](screenshot.png)

## How to Play

Download and install [the latest version of Python](https://www.python.org/downloads/) (will only work on Python v3 and above).  Download all the Python files to the same directory:
- `board.py`
- `chess.py`
- `network.py`
- `pieces.py`

From a command window, type `python chess.py` (or `python3 ` or whatever path has been registered) in the appropriate directory.  This should work on any system that has Python installed.

### Playing locally

Local games are very simple: both players sit at the same terminal and take turns typing in location codes in "algebraic notation" (`a1` or `e7`, for example).  One location code for the starting position and one for the destination.  For the rules of chess, here is an article for beginners: https://www.chess.com/learn-how-to-play-chess

### Playing across a network or the internet

In order to play online, two machines must be used.  The program will ask the following questions:

1. Connect to a remote computer?
1. Act as client or server?
1. What is the remote hostname/IP (client) and port number (client and server)?

After answering these questions, the client will attempt to connect and send a message to the server that is [ideally] waiting to receive a message to test the connection.  The server then sends back a confirmation message, and once the client and server are connected, the server is given the ability to choose white or black (instead referred in this program as `Player #1` and `Player #2` since the whole board is black and all the pieces are white.)  The game then commences and performs the same as the single screen game.

### Notes about playing across the internet

- Playing across the internet requires the server to expose a port on the machine and use port forwarding on your network's router to handle incoming traffic from the client outside the network.  Creating a custom DNS (domain name system) is another option, and sharing a virtual private network (VPN) is a third.
- Security of transmissions is in no way guaranteed!  It is the responsibility of the user to secure their own communications.  Again, the user, by downloading and running `chess.py`, assumes responsibility for any communications whether they are between two terminals on the same small network or two networks over the internet.
- Assuming you read the first two bullet points, there is a product called ngrok (https://ngrok.com/) that allows a user to expose a local port to the internet using reverse SSH tunneling.  Of the options above (port forwarding and custom DNS entries), I believe this technique to be the most secure, except for maybe the VPN.  SSH communications are naturally encrypted, and I believe any communications between the client and ngrok server are encrypted, too.

## Source notes

### `pieces.py`
This file contains several classes modeling the different pieces of a chess board.  There is a `Piece` class that serves as an abstract class for the `Pawn`, `Knight`, `Bishop`, `Rook`, `Queen`, and `King` classes.  The `Piece` class, and it's derivatives, do not contain any information other than their own moves, what side they're on, etc.  Their scope is limited to exclude the board and the players.  

### `board.py`
This file houses the `Board` and `Square` classes.  The `Board` class contains sixty-four instances of the `Square` class in a double-list grid.  Instances of the `Piece` class are attributes of the `Square` class, which, as you might imagine, hold the location information for the occupying piece.  The `Board` class negotiates all moves and evaluates game conditions such as check, checkmate, and stalemate that the other classes cannot simply due to their limited scope.  An instance of the `Board` class is used to hold the information together and is probably the most referenced class during gameplay.

### `network.py`
For communications, Python's socket library was used in two classes: `Client` and `Server`.  One of each of those classes has `connect`, `send`, `receive` and `disconnect` methods.  Because of their similar structure, both players have their own instance of one of the two classes, but both are named `network` to allow ambiguity in the code and cut down on functions that are only slightly different from each other.  As mentioned before, a connection between the client and server is made, and a test "handshake" was written to double check the accuracy of the transmission.  Beyond this initial connection and its subsequent check, all communications are as simple as calling the `send` and `receive` methods.  Other than properly disconnecting, nothing further is required, and the content of each of the messages is limited to four characters: two for the start square and two for the end square.  The dialog between user(s) and the system are also taken care of in this file.

### `chess.py`
This file contains no classes.  There are a couple main loops that cycle through the acceptance of commands from the user.  All commands from the user(s) are processed here, and they all follow the same convention of start square and end square.  This file relies heavily on the `Board` class to work properly.  All movements are processed here.  It effectively acts as a communications buffer to the `Board` class.

## Testing

Many tests were performed to verify the functioning of this game, especially over the internet.  Here are some, but not all, tests:

- Screen showing and changing at the right points in time
- General flow from one screen to the next was smooth
- Only legal moves being allowed, and only illegal moves being prohibited
- Game recognizing 'check', 'checkmate', and 'stalemate' properly and has neither false positives nor false negatives
- All special moves (castling, various pawn moves) working correctly
- Client and server connect and maintain connection throughout gameplay

## Deployment

This GitHub page is the only deployment

## Built With

- [IDLE (Python 3.9 64-bit)](https://www.python.org/)
- [PyCharm Community Edition 2020.3.3 x64](https://www.jetbrains.com/pycharm/)

## Contributing

Please contact me (rbrutherford3) on GitHub in order to inquire more about the project.  My email address is on the home page.

## Versioning

`Git` functions were used to version the software on *GitHub*

## Authors

Robert Rutherford

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Thanks to anyone who was patient with me while I obsessed over this
* Thanks to Victor S for being a valuable soundboard and guide
