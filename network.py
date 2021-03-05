#################################################################
#                                                               #
#       ASCII-Chess, written by Robert Rutherford in 2021       #
#                                                               #
#################################################################


import socket
import time
from abc import ABC, abstractmethod


# Abstract class is used to pass on methods
# that would otherwise be copied and pasted
class Network(ABC):
    host: str
    port: int
    connection: socket
    address: str
    socket: socket

    @abstractmethod
    def connect(self):
        pass

    # Send a message
    def send(self, msg: str):
        self.connection.sendall(msg.encode("UTF-8"))

    # Receive a message (wait until received)
    def receive(self) -> str:
        return self.connection.recv(1024).decode("UTF-8")

    # Kill connection
    def quit(self):
        self.connection.close()


# This class provides server connection commands, plus send and receive commands
# When acting as server, there is no need to specify a remote host, but a port still
# needs to be defined.  One system will act as server, the other as client
class Server(Network):
    host: str = ''  # Symbolic name meaning all available interfaces

    # Set port and create a connection by waiting for the client to connect
    def __init__(self, port: int = 5000):
        self.port = port

    # Create a connection by waiting for a client to connect
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.connection, self.address = self.socket.accept()
        print("Connected by", self.address)


# This class provides client connection commands, plus send and receive commands
# This class can connect to the opponent's server via host/IP and port number
class Client(Network):

    def __init__(self, host: str = "pitunnel3.com", port: int = 37529):
        self.host: str = host
        self.port: int = port

    # Create a connection with server
    def connect(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.host, self.port))


# SET UP USER INTERFACE FOR GAMEPLAY
def accessNetwork():
    # Check if this will be a local game (1 and 2 player at same terminal)
    # or a remote game over the internet
    print("Connect to remote computer? (Y/n)")
    while True:
        onlineGame = input(">").lower()
        if onlineGame == "y":
            onlineGame = True
            break
        elif onlineGame == "n":
            onlineGame = False
            break
        else:
            print("Please enter either \"y\" or \"n\"")

    # Determine whether client or server
    if onlineGame:
        print("Will you act as server (S/s) or client (C/c)?")
        while True:
            networkChoice = input(">").lower()
            if networkChoice == "c" or networkChoice == "s":
                isServer = networkChoice == "s"
                break
            else:
                print("Please enter either \"S\" (or \"s\") or \"C\" (or \"c\")")

        # Create server object (dubbed 'network', same as client)
        # Establish connection criteria (port) and await connection
        if networkChoice == "s":
            while True:  # https://stackoverflow.com/a/56518486
                print("What port will you be using? (leave blank for default of 5000)")
                while True:
                    serverPort = input(">")
                    if not serverPort or serverPort.isnumeric():
                        break
                    else:
                        print(
                            "Please enter a positive whole number (or leave blank for default setting)")
                if not serverPort:
                    network = Server()
                else:
                    network = Server(int(serverPort))
                connected = False
                attempts = 0
                maxAttempts = 15
                while attempts < maxAttempts:
                    try:
                        attempts = attempts + 1
                        print("Attempting to connect...")
                        network.connect()
                        print("Connected!  Testing with a transmission...")
                        break
                    except Exception as e:
                        print(e)
                        time.sleep(1)
                        print("Connection failure, re-attempting (",
                              attempts, "/", maxAttempts, ")")
                while attempts < maxAttempts:
                    try:
                        attempts = attempts + 1
                        if network.receive() == "FUBAR":
                            network.send("FUGAZI")
                            connected = True
                            break
                        else:
                            raise ConnectionError(
                                "Not receiving a response from client")
                    except Exception as e:
                        print(e)
                        time.sleep(1)
                        print("Transmission failure, re-attempting (",
                              attempts, "/", maxAttempts, ")")
                if connected:
                    break
                else:
                    del network
                    print("Please double-check your connection settings")
            print("Success!")

        # Create client object (dubbed 'network', same as server)
        # Establish connection criteria (port and host) and connect
        elif networkChoice == "c":
            while True:
                print(
                    "What host name or IP address will you be using? (leave blank for default)")
                serverHost = input(">")
                if serverHost == "":
                    serverPort = None
                else:
                    print("What port number will you be using? (leave blank for default)")
                    while True:
                        serverPort = input(">")
                        if serverPort == "" or serverPort.isnumeric():
                            break
                        else:
                            print(
                                "Please enter a positive whole number (or leave blank for default setting)")
                if serverHost == "":
                    network = Client()
                else:
                    serverPort = int(serverPort)
                    network = Client(serverHost, serverPort)
                connected = False
                connectionAttempts = 0
                maxConnectionAttempts = 15
                while True:
                    try:
                        print("Attempting to connect...")
                        network.connect()
                        print("Connected!  Testing with a transmission...")
                        network.send("FUBAR")
                        if network.receive() == "FUGAZI":
                            connected = True
                            break
                        else:
                            raise ConnectionError(
                                "Not receiving a response from server")
                    except Exception as e:
                        print(e)
                        connectionAttempts = connectionAttempts + 1
                        print("Connection failure, re-attempting (",
                              connectionAttempts, "/", maxConnectionAttempts, ")")
                        if connectionAttempts >= maxConnectionAttempts:
                            break
                    time.sleep(1)
                if connected:
                    break
                else:
                    del network
                    print("Please double-check your connection settings")
            print("Success!")
            print("The server will choose who plays first, please wait...")

        else:
            raise ValueError("networkChoice should have been \"c\" or \"s\"")

        player = None

        # Server gets first pick of board side
        while True and isServer:
            print("Player 1 or 2?")
            player = input(">")
            if player == "1" or player == "2":
                player = int(player)
                break
            else:
                print("Please enter \"1\" or \"2\" only")

        # Establish other player and send assignment to the client
        if isServer:
            if player == 1:
                otherPlayer = 2
            else:
                otherPlayer = 1
            network.send(str(otherPlayer))
        else:
            print("Waiting for server...")
            player = network.receive()
            if player.isnumeric():
                player = int(player)
                if not (player == 1 or player == 2):
                    raise ValueError(
                        "Server not sending \"1\" or \"2\" for player choice")
            else:
                raise ValueError("Server not sending integers for player choice")
        return network, onlineGame, player
    else:
        return None
