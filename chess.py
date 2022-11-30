#!/usr/bin/python3

#################################################################
#                                                               #
#       ASCII-Chess, written by Robert Rutherford in 2021       #
#                                                               #
#################################################################
# ToDo: fix up dialog between player and network @ beginning
# ToDo: Make back and forth packages more reliable (Maybe serialize board object)
# ToDo: Keep-alive signal?
# ToDo: comments, functions, possibly add a class or two (TDB)

from board import Board, Square
from piecetypes import King, Queen, Bishop, Knight, Rook, Pawn

# Determine whether the string is a code for a square on the board
def isCode(code: str):
    if len(code) == 2:
        char1: str = code[0]
        char2: str = code[1]
        if "a" <= char1.lower() <= "h" and "1" <= char2 <= "8":
            return True
    return False


# Converts user shorthand for squares into row and column tuple for use in program
def deCode(code: str) -> int:
    letters: list[str] = ["a", "b", "c", "d", "e", "f", "g", "h"]
    if len(code) == 2:
        char1: str = code[0]
        char2: str = code[1]
        if "a" <= char1.lower() <= "h" and "1" <= char2 <= "8":
            column: int = letters.index(char1.lower())
            rowNum: int = int(char2) - 1
            return rowNum, column
        else:
            raise ValueError("Location code must contain a upper or lowercase letter " +
                             "from \"a\" to \"h\" first, and a number 1-8 second")
    else:
        raise ValueError("Location code must be two characters")


# This class governs gameplay rules and moves pieces
class Chess(object):
    board: Board
    msg: str = ""
    currentPlayer: int = 1
    startSquare: Square
    endSquare: Square
    inCheck: bool
    gameOn: bool = True


    def __init__(self):
        self.board = Board()
        self.board.setup()


    # Run through every possible error that could result from this move, return blank and move pieces if none
    def movePiece(self, newStart: str, newEnd: str, player: int) -> str:
        if player != 1 and player != 2:
            return "Your code does not match either player, please try again"
        if player != self.currentPlayer:
            return "Not yet your turn, please wait"
        if isCode(newStart):
            startLocation = deCode(newStart)
        else:
            return "Please type column letter then row number"
        if Square.isSquare(startLocation[0], startLocation[1]):
            self.startSquare = self.board.getSquare(startLocation[0], startLocation[1])
        else:
            return "Please choose a square on the board"
        if self.startSquare.piece.player != self.currentPlayer:
            return "Please choose your own piece"
        if isCode(newEnd):
            endLocation = deCode(newEnd)
        else:
            return "Please type column letter then row number"
        if Square.isSquare(endLocation[0], endLocation[1]):
            self.endSquare = self.board.getSquare(endLocation[0], endLocation[1])
        else:
            return "Please choose a square on the board"
        if self.endSquare.piece is not None and self.endSquare.piece.player == self.currentPlayer:
            return "Please move to an empty square or capture a piece"
        legalMoves = self.findLegalMoves()
        if self.endSquare not in legalMoves:
            return "Move is illegal"
        if isinstance(self.startSquare.piece, King) and abs(self.endSquare.column - self.startSquare.column) == 2:
            return self.castle()
        if isinstance(self.startSquare.piece, Pawn):
            self.markEnPassant()
            if self.isEnPassantAttempt():
                return self.enPassant()
        savedPiece = self.endSquare.piece
        self.endSquare.piece = self.startSquare.piece
        self.startSquare.piece = None
        if self.board.check(self.currentPlayer):
            self.startSquare.piece = self.endSquare.piece
            self.endSquare.piece = savedPiece
            return "This move places you in check, please try again"
        self.endSquare.piece.moved = True
        return ""

    def drawBoard(self, player: int) -> str:
        return self.board.draw(player)

    def switchPlayers(self):
        self.currentPlayer = Square.opponent(self.currentPlayer)

    # Gather moves possibilities for special pieces and all other pieces, too
    def findLegalMoves(self) -> frozenset:
        if isinstance(self.startSquare.piece, Pawn):
            return self.board.getPawnMoves(self.startSquare)
        elif isinstance(self.startSquare.piece, King):
            return self.board.getMoves(self.startSquare).union(self.board.getKingMoves(self.currentPlayer))
        else:
            return self.board.getMoves(self.startSquare)

    # See if a pawn made it to the other side for a piece promotion
    def promotePawnCheck(self) -> bool:
        if isinstance(self.endSquare.piece, Pawn) and (
                (self.endSquare.piece.player == 1 and self.endSquare.row == 7) or
                (self.endSquare.piece.player == 2 and self.endSquare.row == 0)):
            return True
        else:
            return False

    # Apply the promotion selected for the pawn
    def promotePawn(self, promotion: str) -> str:
        if promotion == "1":
            self.endSquare.piece = Queen(self.currentPlayer)
        elif promotion == "2":
            self.endSquare.piece = Bishop(self.currentPlayer)
        elif promotion == "3":
            self.endSquare.piece = Knight(self.currentPlayer)
        elif promotion == "4":
            self.endSquare.piece = Rook(self.currentPlayer)
        else:
            return "Invalid selection, please try again"
        return ""

    # See if game is over or not.  Be sure to cover this before and after a move
    def gameStatus(self, player) -> str:
        if self.board.check(self.currentPlayer):
            if self.board.checkmate(self.currentPlayer):
                self.gameOn = False
                if player == self.currentPlayer:
                    return "<h3 style=\"color: red;\">Checkmate!  You lose!</h3>"
                else:
                    return "<h3 style=\"color: green;\">Checkmate!  You win!</h3>"
            else:
                if player == self.currentPlayer:
                    return "<h3 style=\"color: red;\">You are in check!</h3>"
                else:
                    return "<h3 style=\"color: green;\">You placed your opponent in check!</h3>"
        elif self.board.stalemate(self.currentPlayer):
            self.gameOn = False
            return "<h3 style=\"color: blue;\">No legal moves left!  Stalemate</h3>"
        return ""

    # If the king moved two spaces laterally, see if a castling move is possible (first move, no spaces in check, clear)
    def castle(self) -> str:
        if not isinstance(self.startSquare.piece, King):
            return "No king at start square!"
        if abs(self.startSquare.column - self.endSquare.column) != 2:
            return "End square input must be either two to the left or right of the king"
        row = self.endSquare.row
        if self.endSquare.column <= 3:
            column = 0
            columnChange = 3
        else:
            column = 7
            columnChange = -2
        rookStartSquare = self.board.getSquare(row, column)
        if not isinstance(rookStartSquare.piece, Rook):
            return "No rook found for castle move!"
        self.endSquare.piece = self.startSquare.piece
        self.startSquare.piece = None
        self.endSquare.piece.moved = True
        rookEndSquare = self.board.getSquare(row, column + columnChange)
        rookEndSquare.piece = rookStartSquare.piece
        rookStartSquare.piece = None
        rookEndSquare.piece.moved = True
        return ""

    # If a pawn moved two spaces, it could still be taken by an opposing pawn diagonally moving to the skipped square
    def markEnPassant(self):
        if isinstance(self.startSquare.piece, Pawn) and \
                abs(self.endSquare.row - self.startSquare.row) == 2:
            self.startSquare.piece.enPassant = True
        else:
            self.startSquare.piece.enPassant = False

    # Check if an en passant move is being attempted (rare)
    def isEnPassantAttempt(self) -> bool:
        return isinstance(self.startSquare.piece, Pawn) \
               and self.endSquare.column != self.startSquare.column and \
               self.endSquare.piece is None

    # Apply the en passant move only after a thorough check that it is legal
    def enPassant(self):
        enPassant = self.board.getSquare(self.startSquare.row, self.endSquare.column)
        if enPassant.piece is not None and \
                isinstance(enPassant.piece, Pawn) and \
                enPassant.piece.player == Square.opponent(self.currentPlayer) and \
                enPassant.piece.enPassant:
            self.endSquare.piece = self.startSquare.piece
            self.startSquare.piece = None
            enPassant.piece = None
            return ""
        else:
            return "Not a valid en Passant move"
