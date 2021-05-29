#################################################################
#                                                               #
#       ASCII-Chess, written by Robert Rutherford in 2021       #
#                                                               #
#################################################################
from time import sleep
import urllib3


# Class used to communicate with a remote player
class Network:
    http: urllib3
    host: str = 'spiffindustries.com/chess'
    filename: str = 'chess_move.php'
    url: str
    player: int
    msg: str
    lastId: int = None

    # Constructor: establish connection string.
    def __init__(self):
        self.http = urllib3.PoolManager()
        if self.host.endswith('/'):
            self.url = self.host + self.filename
        else:
            self.url = self.host + '/' + self.filename

    # Assign sides randomly at the beginning of the game
    def newGame(self) -> int:
        r = self.http.request('GET', self.url + '?newGame')
        msg = r.data.decode("utf-8")
        if msg == 'white':
            self.player = 1
        elif msg == 'black':
            self.player = 2
        else:
            raise Exception('Initiating new game failed')
        return self.player

    def readyToStart(self):
        print('Waiting for opponent to join...')
        while True:
            r = self.http.request('GET', self.url + '?readyToStart')
            msg = r.data.decode("utf-8")
            if msg == 'WAIT':
                sleep(1)
            else:
                break
        return True

    # Transmit last move to remote player
    def sendMove(self, row1: int, col1: int, row2: int, col2: int) -> str:
        r = self.http.request('GET', self.url + '?player=' + str(self.player) +
                              '&row1=' + str(row1) + '&col1=' + str(col1) +
                              '&row2=' + str(row2) + '&col2=' + str(col2))
        msg = r.data.decode('utf-8')
        return msg

    # Receiving move transmission from remote player
    def receiveMove(self, lastId: int) -> str:
        while True:
            r = self.http.request('GET', self.url + '?id=' + str(lastId))
            msg = r.data.decode('utf-8')
            if msg == 'WAIT':
                sleep(1)
            else:
                break
        return msg
