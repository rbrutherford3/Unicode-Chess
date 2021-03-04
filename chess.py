#################################################################
#                                                               #
#       ASCII-Chess, written by Robert Rutherford in 2021       #
#                                                               #
#################################################################
# ToDo: fix up dialog between player and network @ beginning
# ToDo: Make back and forth packages more reliable (Maybe serialize board object)
# ToDo: Keepalive signal?
# ToDo: comments, functions, possibly add a class or two (TDB)


import socket
import time
from abc import ABC
from os import system, name


# define our clear function (https://www.geeksforgeeks.org/clear-screen-python/)
def clear():
    # for windows
    if name == "nt":
        _ = system("cls")

        # for mac and linux(here, os.name is 'posix')
    else:
        _ = system("clear")


# Abstract class to model chess pieces by providing necessary attributes
class Piece(ABC):
    name: str  # name of piece, i.e.: 'king'
    symbol: str  # shorthand of piece for display on board
    value: int  # algebraic value (not used)
    player: int  # belongs to player 1 or 2
    moves: frozenset  # all the legal moves for the piece, as vectors
    scalable: bool  # can piece move freely along a given path (i.e.: queen)?
    # does this piece have moves outside of the norm (i.e.: castling)
    specialMoves: bool
    # monitor if the piece has moved at all (for castling only)
    moved: bool = False

    # start with player number
    def __init__(self, thisPlayer: int):
        self.player: int = thisPlayer


# Pawn class (note that all pawn moves are atypical, to a strange
# degree, so no 'typical' moves are listed)
class Pawn(Piece):
    name = "pawn"
    symbol = "p"
    value = 1
    moves = None  # all pawn movements are affected by surrounding pieces
    scalable = False
    specialMoves = frozenset([(1, 0), (1, 1), (1, -1), (2, 0)])


# Knight class
class Knight(Piece):
    name = "knight"
    symbol = "N"
    value = 3
    moves = frozenset([(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2),
                       (-1, -2), (1, -2)])
    scalable = False
    specialMoves = False


# Bishop class
class Bishop(Piece):
    name = "bishop"
    symbol = "B"
    value = 3
    moves = frozenset([(1, 1), (1, -1), (-1, -1), (-1, 1)])
    scalable = True
    specialMoves = False


# Rook class (note that it is not marked as special because it can't
# initiate castling, only follows it)
class Rook(Piece):
    name = "rook"
    symbol = "R"
    value = 5
    moves = frozenset([(1, 0), (-1, 0), (0, 1), (0, -1)])
    scalable = True
    specialMoves = frozenset([(0, 3), (0, -2)])


# Queen class
class Queen(Piece):
    name = "queen"
    symbol = "Q"
    value = 9
    moves = frozenset([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1),
                       (-1, -1), (-1, 1)])
    scalable = True
    specialMoves = False


# King class
class King(Piece):
    def __init__(self, thisPlayer: int):
        super().__init__(thisPlayer)
        self.location = None

    name = "king"
    symbol = "K"
    value = None
    moves = frozenset([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1),
                       (-1, -1), (-1, 1)])
    scalable = False
    specialMoves = frozenset([(0, -2), (0, 2)])


# Class that represents one square on a board (note that indexing
# in Python is from 0, so translation is required)
class Square(object):
    row: int
    column: int
    piece: Piece

    # Can be initiated with or without an occupying piece
    def __init__(self, thisRow, thisColumn, thisPiece=None):
        self.row = thisRow
        self.column = thisColumn
        self.piece = thisPiece

    # Over-riding 'to string' function for displaying on board
    def __str__(self):
        if self.piece is None:
            return "---"
        else:
            return str(self.piece.player) + "_" + self.piece.symbol

    # Add a piece after instantiation
    def setPiece(self, piece: Piece):
        self.piece = piece


# Converts user shorthand for squares into row and column tuple for use in program
def decode(code: str):  # -> Optional[tuple[int, int]]:
    letters: list[str] = ["a", "b", "c", "d", "e", "f", "g", "h"]
    if len(code) == 2:
        char1: str = code[0]
        char2: str = code[1]
        if "a" <= char1.lower() <= "h" and "1" <= char2 <= "8":
            column: int = letters.index(char1.lower())
            row: int = int(char2) - 1
            return row, column
        else:
            return None
    else:
        return None


# Yield the opposite player
def opponent(player):
    if player == 1:
        return 2
    elif player == 2:
        return 1
    else:
        raise ValueError("Players are either 1 or 2")


# Board class, which holds most functioning and is composed of 64 square objects
class Board(object):  # Square objects are assigned a location on a
    grid: list  # [list[Square]] # two-dimensional gridded 'board'
    numRows: int = 8
    numColumns: int = 8

    opponent = opponent  # stealing function for getting the opposite player

    # Begin by initiating grid
    def __init__(self):
        self.grid = [[
            Square(gridRow, gridColumn)
            for gridColumn in range(self.numColumns)
        ] for gridRow in range(self.numRows)]

        self.King1 = King(1)
        self.King2 = King(2)

    def getKing(self, player) -> King:
        if player == 1:
            return self.King1
        elif player == 2:
            return self.King2
        else:
            raise ValueError("Player can be either 1 or 2")

    # This method sets up each individual piece on the 'grid'
    def setup(self):

        [self.grid[1][column].setPiece(Pawn(1))
         for column in range(self.numColumns)]
        [self.grid[6][column].setPiece(Pawn(2))
         for column in range(self.numColumns)]
        [self.grid[0][column].setPiece(Rook(1)) for column in [0, 7]]
        [self.grid[7][column].setPiece(Rook(2)) for column in [0, 7]]
        [self.grid[0][column].setPiece(Knight(1)) for column in [1, 6]]
        [self.grid[7][column].setPiece(Knight(2)) for column in [1, 6]]
        [self.grid[0][column].setPiece(Bishop(1)) for column in [2, 5]]
        [self.grid[7][column].setPiece(Bishop(2)) for column in [2, 5]]
        self.grid[0][3].setPiece(Queen(1))
        self.grid[7][3].setPiece(Queen(2))
        self.grid[0][4].setPiece(self.King1)
        self.King1.location = self.grid[0][4]
        self.grid[7][4].setPiece(self.King2)
        self.King2.location = self.grid[7][4]

    # Draw the board onto the screen with unicode ASCII characters (old school, yes)
    def draw(self, player: int):

        if (player == 1):
            print("")
            print("        a       b       c       d       e       f       g       h")
            print("    -----------------------------------------------------------------")
            print("    |       |///////|       |///////|       |///////|       |///////|")
            print(" 8  |  " + str(self.grid[7][0]) + "  |//" + str(self.grid[7][1]) +
                  "//|  " + str(self.grid[7][2]) + "  |//" + str(self.grid[7][3]) +
                  "//|  " + str(self.grid[7][4]) + "  |//" + str(self.grid[7][5]) +
                  "//|  " + str(self.grid[7][6]) + "  |//" + str(self.grid[7][7]) + "//|  8")
            print("    |       |///////|       |///////|       |///////|       |///////|")
            print("    -----------------------------------------------------------------")
            print("    |///////|       |///////|       |///////|       |///////|       |")
            print(" 7  |//" + str(self.grid[6][0]) + "//|  " + str(self.grid[6][1]) +
                  "  |//" + str(self.grid[6][2]) + "//|  " + str(self.grid[6][3]) +
                  "  |//" + str(self.grid[6][4]) + "//|  " + str(self.grid[6][5]) +
                  "  |//" + str(self.grid[6][6]) + "//|  " + str(self.grid[6][7]) + "  |  7")
            print("    |///////|       |///////|       |///////|       |///////|       |")
            print("    -----------------------------------------------------------------")
            print("    |       |///////|       |///////|       |///////|       |///////|")
            print(" 6  |  " + str(self.grid[5][0]) + "  |//" + str(self.grid[5][1]) +
                  "//|  " + str(self.grid[5][2]) + "  |//" + str(self.grid[5][3]) +
                  "//|  " + str(self.grid[5][4]) + "  |//" + str(self.grid[5][5]) +
                  "//|  " + str(self.grid[5][6]) + "  |//" + str(self.grid[5][7]) + "//|  6")
            print("    |       |///////|       |///////|       |///////|       |///////|")
            print("    -----------------------------------------------------------------")
            print("    |///////|       |///////|       |///////|       |///////|       |")
            print(" 5  |//" + str(self.grid[4][0]) + "//|  " + str(self.grid[4][1]) +
                  "  |//" + str(self.grid[4][2]) + "//|  " + str(self.grid[4][3]) +
                  "  |//" + str(self.grid[4][4]) + "//|  " + str(self.grid[4][5]) +
                  "  |//" + str(self.grid[4][6]) + "//|  " + str(self.grid[4][7]) + "  |  5")
            print("    |///////|       |///////|       |///////|       |///////|       |")
            print("    -----------------------------------------------------------------")
            print("    |       |///////|       |///////|       |///////|       |///////|")
            print(" 4  |  " + str(self.grid[3][0]) + "  |//" + str(self.grid[3][1]) +
                  "//|  " + str(self.grid[3][2]) + "  |//" + str(self.grid[3][3]) +
                  "//|  " + str(self.grid[3][4]) + "  |//" + str(self.grid[3][5]) +
                  "//|  " + str(self.grid[3][6]) + "  |//" + str(self.grid[3][7]) + "//|  4")
            print("    |       |///////|       |///////|       |///////|       |///////|")
            print("    -----------------------------------------------------------------")
            print("    |///////|       |///////|       |///////|       |///////|       |")
            print(" 3  |//" + str(self.grid[2][0]) + "//|  " + str(self.grid[2][1]) +
                  "  |//" + str(self.grid[2][2]) + "//|  " + str(self.grid[2][3]) +
                  "  |//" + str(self.grid[2][4]) + "//|  " + str(self.grid[2][5]) +
                  "  |//" + str(self.grid[2][6]) + "//|  " + str(self.grid[2][7]) + "  |  3")
            print("    |///////|       |///////|       |///////|       |///////|       |")
            print("    -----------------------------------------------------------------")
            print("    |       |///////|       |///////|       |///////|       |///////|")
            print(" 2  |  " + str(self.grid[1][0]) + "  |//" + str(self.grid[1][1]) +
                  "//|  " + str(self.grid[1][2]) + "  |//" + str(self.grid[1][3]) +
                  "//|  " + str(self.grid[1][4]) + "  |//" + str(self.grid[1][5]) +
                  "//|  " + str(self.grid[1][6]) + "  |//" + str(self.grid[1][7]) + "//|  2")
            print("    |       |///////|       |///////|       |///////|       |///////|")
            print("    -----------------------------------------------------------------")
            print("    |///////|       |///////|       |///////|       |///////|       |")
            print(" 1  |//" + str(self.grid[0][0]) + "//|  " + str(self.grid[0][1]) +
                  "  |//" + str(self.grid[0][2]) + "//|  " + str(self.grid[0][3]) +
                  "  |//" + str(self.grid[0][4]) + "//|  " + str(self.grid[0][5]) +
                  "  |//" + str(self.grid[0][6]) + "//|  " + str(self.grid[0][7]) + "  |  1")
            print("    |///////|       |///////|       |///////|       |///////|       |")
            print("    -----------------------------------------------------------------")
            print("        a       b       c       d       e       f       g       h")
            print("")

        # Show board from the other side for player 2
        elif (player == 2):
            print("")
            print("        h       g       f       e       d       c       b       a")
            print("    -----------------------------------------------------------------")
            print("    |       |///////|       |///////|       |///////|       |///////|")
            print(" 1  |  " + str(self.grid[0][7]) + "  |//" + str(self.grid[0][6]) +
                  "//|  " + str(self.grid[0][5]) + "  |//" + str(self.grid[0][4]) +
                  "//|  " + str(self.grid[0][3]) + "  |//" + str(self.grid[0][2]) +
                  "//|  " + str(self.grid[0][1]) + "  |//" + str(self.grid[0][0]) + "//|  1")
            print("    |       |///////|       |///////|       |///////|       |///////|")
            print("    -----------------------------------------------------------------")
            print("    |///////|       |///////|       |///////|       |///////|       |")
            print(" 2  |//" + str(self.grid[1][7]) + "//|  " + str(self.grid[1][6]) +
                  "  |//" + str(self.grid[1][5]) + "//|  " + str(self.grid[1][4]) +
                  "  |//" + str(self.grid[1][3]) + "//|  " + str(self.grid[1][2]) +
                  "  |//" + str(self.grid[1][1]) + "//|  " + str(self.grid[1][0]) + "  |  2")
            print("    |///////|       |///////|       |///////|       |///////|       |")
            print("    -----------------------------------------------------------------")
            print("    |       |///////|       |///////|       |///////|       |///////|")
            print(" 3  |  " + str(self.grid[2][7]) + "  |//" + str(self.grid[2][6]) +
                  "//|  " + str(self.grid[2][5]) + "  |//" + str(self.grid[2][4]) +
                  "//|  " + str(self.grid[2][3]) + "  |//" + str(self.grid[2][2]) +
                  "//|  " + str(self.grid[2][1]) + "  |//" + str(self.grid[2][0]) + "//|  3")
            print("    |       |///////|       |///////|       |///////|       |///////|")
            print("    -----------------------------------------------------------------")
            print("    |///////|       |///////|       |///////|       |///////|       |")
            print(" 4  |//" + str(self.grid[3][7]) + "//|  " + str(self.grid[3][6]) +
                  "  |//" + str(self.grid[3][5]) + "//|  " + str(self.grid[3][4]) +
                  "  |//" + str(self.grid[3][3]) + "//|  " + str(self.grid[3][2]) +
                  "  |//" + str(self.grid[3][1]) + "//|  " + str(self.grid[3][0]) + "  |  4")
            print("    |///////|       |///////|       |///////|       |///////|       |")
            print("    -----------------------------------------------------------------")
            print("    |       |///////|       |///////|       |///////|       |///////|")
            print(" 5  |  " + str(self.grid[4][7]) + "  |//" + str(self.grid[4][6]) +
                  "//|  " + str(self.grid[4][5]) + "  |//" + str(self.grid[4][4]) +
                  "//|  " + str(self.grid[4][3]) + "  |//" + str(self.grid[4][2]) +
                  "//|  " + str(self.grid[4][1]) + "  |//" + str(self.grid[4][0]) + "//|  5")
            print("    |       |///////|       |///////|       |///////|       |///////|")
            print("    -----------------------------------------------------------------")
            print("    |///////|       |///////|       |///////|       |///////|       |")
            print(" 6  |//" + str(self.grid[5][7]) + "//|  " + str(self.grid[5][6]) +
                  "  |//" + str(self.grid[5][5]) + "//|  " + str(self.grid[5][4]) +
                  "  |//" + str(self.grid[5][3]) + "//|  " + str(self.grid[5][2]) +
                  "  |//" + str(self.grid[5][1]) + "//|  " + str(self.grid[5][0]) + "  |  6")
            print("    |///////|       |///////|       |///////|       |///////|       |")
            print("    -----------------------------------------------------------------")
            print("    |       |///////|       |///////|       |///////|       |///////|")
            print(" 7  |  " + str(self.grid[6][7]) + "  |//" + str(self.grid[6][6]) +
                  "//|  " + str(self.grid[6][5]) + "  |//" + str(self.grid[6][4]) +
                  "//|  " + str(self.grid[6][3]) + "  |//" + str(self.grid[6][2]) +
                  "//|  " + str(self.grid[6][1]) + "  |//" + str(self.grid[6][0]) + "//|  7")
            print("    |       |///////|       |///////|       |///////|       |///////|")
            print("    -----------------------------------------------------------------")
            print("    |///////|       |///////|       |///////|       |///////|       |")
            print(" 8  |//" + str(self.grid[7][7]) + "//|  " + str(self.grid[7][6]) +
                  "  |//" + str(self.grid[7][5]) + "//|  " + str(self.grid[7][4]) +
                  "  |//" + str(self.grid[7][3]) + "//|  " + str(self.grid[7][2]) +
                  "  |//" + str(self.grid[7][1]) + "//|  " + str(self.grid[7][0]) + "  |  8")
            print("    |///////|       |///////|       |///////|       |///////|       |")
            print("    -----------------------------------------------------------------")
            print("        h       g       f       e       d       c       b       a")
            print("")
        else:
            raise ValueError("Need input of 1 or 2")

    # Reference a particular square on the grid
    def getSquare(self, row: int, column: int) -> Square:
        if row in range(self.numRows) and column in range(self.numColumns):
            return self.grid[row][column]
        else:
            return None  # raise ValueError("Please use 0-7 indices")

    # Get all possible moves (even if capturing an piece)
    # For this to work, the piece is "walked" along the board until
    # it runs out or hits an opponent or neighbor
    def getMoves(self, start: Square) -> frozenset:
        if start is None:
            return frozenset()
        else:
            if start.piece is None:
                return frozenset()
            else:
                if start.piece.moves is None:
                    return frozenset()
                else:
                    moves = frozenset()
                    player: int = start.piece.player
                    otherPlayer: int = opponent(player)

                    # Grab all movement directions applicable to the piece
                    for vector in start.piece.moves:
                        square = start  # need for initial condition

                        # Move along the direction of the move (dubbed vector)
                        while True:
                            row = square.row + vector[0]
                            column = square.column + vector[1]
                            square = self.getSquare(row, column)
                            if square is None:  # Walk until hitting an edge
                                break
                            else:
                                if square.piece is None:
                                    moves = moves.union([square])
                                    if not start.piece.scalable:  # Stop if limited to move one square only
                                        break
                                # Stop if opponent is encountered (capture)
                                elif square.piece.player == otherPlayer:
                                    moves = moves.union([square])
                                    break
                                else:  # Go until the end
                                    break
                    return moves

    # Pawns are unique in only moving one direction, capturing pieces at an angle, and more
    # as a result, they have their own method for movement
    def getPawnMoves(self, square: Square) -> frozenset:
        moves = frozenset()
        if square is None:
            return moves
        if square.piece is None:
            return moves
        if isinstance(square.piece, Pawn):
            row = square.row
            column = square.column
            player = square.piece.player

            # Work with both sides, which have opposing directions
            if player == 1:
                direction = 1
            else:
                direction = -1

            # Portray a typical move one square forward movement
            forward = self.getSquare(row + 1 * direction, column)
            if forward.piece is None:
                moves = moves.union([forward])

            # Include the moves for capturing pieces at an angle, dubbed east and west here
            east = self.getSquare(row + 1 * direction, column + 1)
            west = self.getSquare(row + 1 * direction, column - 1)
            threat = False  # "Threat" implies that there are pieces in those slots

            # Add the move ONLY if there is an opposing player's piece in those diagonal slots
            if east is not None:
                if east.piece is not None:
                    if east.piece.player == opponent(player):
                        moves = moves.union([east])
                        threat = True

            # For both sides...
            if west is not None:
                if west.piece is not None:
                    if west.piece.player == opponent(player):
                        moves = moves.union([west])
                        threat = True

            # At this point, we must evaluate whether the two square forward move is eligible
            # (must be first move and not bypass any of the opposing player's pieces
            if threat or square.piece.moved or forward.piece is not None:
                return moves
            else:
                forwardTwo = self.getSquare(row + 2 * direction, column)
                if forwardTwo is not None:
                    if forwardTwo.piece is None:
                        moves = moves.union([forwardTwo])
                        return moves
                return moves
        else:
            raise ValueError("Square does not contain a pawn")

    # Other than the typical moves, a king has castling opportunities
    # There are two castling directions: King-side (4 squares wide) and Queen-side (5 squares wide)
    # This method adds those moves only if they are eligible (not in check, path clear, etc)
    def getKingMoves(self, player: int) -> frozenset:
        moves = frozenset()
        king = self.getKing(player)
        if king.moved:
            return frozenset()
        row = king.location.row
        kingColumn = king.location.column
        rookColumn = 7
        firstMove = self.getSquare(row, kingColumn + 1)
        secondMove = self.getSquare(row, kingColumn + 2)
        rookSquare = self.getSquare(row, rookColumn)
        if rookSquare is not None and rookSquare.piece is not None and \
                isinstance(rookSquare.piece, Rook) and not rookSquare.piece.moved and \
                firstMove is not None and firstMove.piece is None and \
                secondMove is not None or secondMove.piece is None:
            moves = moves.union([secondMove])
        rookColumn = 0
        firstMove = self.getSquare(row, kingColumn - 1)
        secondMove = self.getSquare(row, kingColumn - 2)
        thirdMove = self.getSquare(row, kingColumn - 3)
        rookSquare = self.getSquare(row, rookColumn)
        if rookSquare is not None and rookSquare.piece is not None and \
                isinstance(rookSquare.piece, Rook) and not rookSquare.piece.moved and \
                firstMove is not None and firstMove.piece is None and \
                secondMove is not None or secondMove.piece is None and \
                thirdMove is not None and thirdMove.piece is None:
            moves = moves.union([secondMove])
        return moves

    # Combines all possible moves from one player to see where
    # the opponent's king would be in check or not
    def checkZone(self, aggressor: int) -> frozenset:
        checkZone = frozenset()
        for checkRow in self.grid:
            for checkSquare in checkRow:
                if checkSquare.piece is not None:
                    if checkSquare.piece.player == aggressor:
                        # Again, pawns are unique in their movements, so they are added separately
                        if isinstance(checkSquare.piece, Pawn):
                            if aggressor == 1:
                                eastSquare = self.getSquare(
                                    checkSquare.row + 1,
                                    checkSquare.column + 1)
                                westSquare = self.getSquare(
                                    checkSquare.row + 1,
                                    checkSquare.column - 1)
                            else:
                                eastSquare = self.getSquare(
                                    checkSquare.row - 1,
                                    checkSquare.column + 1)
                                westSquare = self.getSquare(
                                    checkSquare.row - 1,
                                    checkSquare.column - 1)
                            if eastSquare is not None:
                                checkZone = checkZone.union([eastSquare])
                            if westSquare is not None:
                                checkZone = checkZone.union([westSquare])
                        else:
                            checkZone = checkZone.union(
                                self.getMoves(checkSquare))
        return checkZone

    # Applies the above method to a specific piece
    def check(self, player: int) -> bool:
        return self.getKing(player).location in self.checkZone(opponent(player))

    # For all moves on one side, move each piece once to see if the king would still be in check (checkmate)
    # The pieces are walked back from the check to preserve the layout
    # Castling is not considered due to check restrictions:
    # "cannot castle into, out of, or through check"
    def checkmate(self, forPlayer: int) -> bool:
        checkmated = True
        for row in self.grid:
            for square in row:
                if square.piece is not None and square.piece.player == forPlayer:
                    if isinstance(square.piece, Pawn):
                        testMoves = self.getPawnMoves(square)
                    else:
                        testMoves = self.getMoves(square)
                    if testMoves is not None:
                        for move in testMoves:
                            pieceSaved = False
                            savedPiece = None
                            if move.piece is not None:
                                pieceSaved = True
                                savedPiece = move.piece
                            move.piece = square.piece
                            square.piece = None
                            if isinstance(move.piece, King):
                                self.getKing(forPlayer).location = move
                            if not self.check(forPlayer):
                                checkmated = False
                            square.piece = move.piece
                            if isinstance(square.piece, King):
                                self.getKing(forPlayer).location = square
                            if pieceSaved:
                                move.piece = savedPiece
                            else:
                                move.piece = None
        return checkmated

    # If no moves are possible for a given side, then there is a stalemate
    def stalemate(self, player: int) -> bool:
        stalemate = False
        moves = frozenset()
        for row in self.grid:
            for square in row:
                if square is not None:
                    if square.piece is not None:
                        if square.piece.player == player:
                            if isinstance(square.piece, King):
                                moves = moves.union(
                                    self.getMoves(square).union(
                                        self.getKingMoves(player)))
                            elif isinstance(square.piece, Pawn):
                                moves = moves.union(self.getPawnMoves(square))
                            else:
                                moves = moves.union(self.getMoves(square))
        if len(moves) == 0:
            stalemate = True
        return stalemate


# This class provides server connection commands, plus send and receive commands
# When acting as server, there is no need to specify a remote host, but a port still
# needs to be defined.  One system will act as server, the other as client
class Server(object):
    HOST: str = ''  # Symbolic name meaning all available interfaces
    PORT: int  # Arbitrary non-privileged port

    # Set port and create a connection by waiting for the client to connect
    def __init__(self, portChoice: int = 5000):
        self.PORT = portChoice

    # Create a connection by waiting for a client to connect
    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.HOST, self.PORT))
        self.s.listen(1)
        self.conn, self.addr = self.s.accept()
        print("Connected by", self.addr)

    # Send a message
    def send(self, msg: str):
        self.conn.sendall(msg.encode("UTF-8"))

    # Receive a message (wait until received)
    def receive(self) -> str:
        self.data = self.conn.recv(1024)
        return self.data.decode("UTF-8")

    # Kill connection
    def quit(self):
        self.conn.close()


# This class provides client connection commands, plus send and receive commands
# This class can connect to the opponent's server via host/IP and port number
class Client(object):
    HOST: str  # The remote host
    PORT: int  # The same port as used by the server

    def __init__(self, hostChoice: str = "pitunnel3.com", portChoice: int = 34757):
        self.HOST: str = hostChoice
        self.PORT: int = portChoice

    # Create a connection with server
    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.HOST, self.PORT))

    # Send a message to the server
    def send(self, msg):
        self.s.sendall(msg.encode("UTF-8"))

    # Wait for a message from the server
    def receive(self) -> str:
        data = self.s.recv(1024)
        return data.decode("UTF-8")

    # Kill connection
    def quit(self):
        self.s.close()


# SET UP USER INTERFACE FOR GAMEPLAY

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
    # Establish connection critera (port) and await connection
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
    # Establish connection critera (port and host) and connect
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
        raise ValueError("networkChoice should have beeen \"c\" or \"s\"")

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
            if player == 1:
                otherPlayer = 2
            elif player == 2:
                otherPlayer = 1
            else:
                raise ValueError(
                    "Server not sending \"1\" or \"2\" for player choice")
        else:
            raise ValueError("Server not sending integers for player choice")


# Because this is over a connection and two instances of this program
# will be running, it is important to establish between the two whose turn it is
currentPlayer = 1
currentOtherPlayer = 2

# Set up board
board = Board()
board.setup()
gameOn = True
firstMove = onlineGame  # only need this if playing remotely to sync players

# Keep looping through turns until the game ends
while gameOn:

    # Re-draw the board (in the corrent orientation)
    clear()
    if onlineGame:
        board.draw(player)
    else:
        board.draw(currentPlayer)

    # Begin processing moves!
    if not onlineGame or (onlineGame and currentPlayer == player):

        # Check to see if there was a game ending situation for defender
        inCheck = False
        king = board.getKing(currentPlayer)
        if board.check(currentPlayer):
            if board.checkmate(currentPlayer):
                print("Checkmate!  You lose!")
                gameOn = False
            else:
                inCheck = True
                print("You are in check!")
        elif board.stalemate(currentPlayer):
            print("No legal moves left!  Stalemate")
            gameOn = False

        # ToDo: consider deleting this and tracing route for losing player
        if not gameOn:
            if onlineGame:
                network.quit()
            break

        # ToDo: re-indent?
        # Cycle through user input for moves (square for beginning, square for ending)
        while gameOn:

            # Loop until beginning square is established
            while gameOn:
                print("Player #", currentPlayer)
                print("Select piece")
                startCode = input(">")
                startLocation = decode(startCode)
                if startLocation is None:
                    print("Please type column letter then row number")
                else:
                    startSquare = board.getSquare(startLocation[0],
                                                  startLocation[1])
                    if startSquare is None:
                        print("Please choose a square on the board")
                    else:
                        if startSquare.piece is None:
                            print("Please choose a square with a piece on it")
                        else:
                            if startSquare.piece.player == currentPlayer:
                                break
                            else:
                                print("Please select a player on your own side")

            # Gather moves possibilities for special pieces and all other pieces, too
            if isinstance(startSquare.piece, Pawn):
                moves = board.getPawnMoves(startSquare)
            elif isinstance(startSquare.piece, King):
                moves = board.getMoves(startSquare).union(
                    board.getKingMoves(currentPlayer))
            else:
                moves = board.getMoves(startSquare)
            print("Select move")
            endCode = input(">")
            endLocation = decode(endCode)
            if endLocation is None:
                print("Please type column letter then row number")
            else:
                endSquare = board.getSquare(endLocation[0], endLocation[1])
                if endSquare is None:
                    print("Please choose a square on the board")
                else:
                    if moves == frozenset():  # this line doesn't seem to work well
                        print(
                            "No moves available for this piece, please try again")
                    else:
                        if endSquare in moves:
                            # ToDo: need logic for check situations
                            # if castling...
                            if isinstance(startSquare.piece, King) and \
                                    abs(endSquare.column - startSquare.column) == 2:
                                endSquare.piece = startSquare.piece
                                king.location = endSquare
                                startSquare.piece = None
                                row = endSquare.row
                                if endSquare.column <= 3:
                                    rookColumn = 0
                                    rookColumnMove = 3
                                else:
                                    rookColumn = 7
                                    rookColumnMove = -2
                                rookStartSquare = board.getSquare(
                                    row, rookColumn)
                                rookEndSquare = board.getSquare(
                                    row, rookColumn + rookColumnMove)
                                rookEndSquare.piece = rookStartSquare.piece
                                rookStartSquare.piece = None
                                rookEndSquare
                                rookEndSquare.piece.moved = True
                                king.moved = True

                            # If pawn reaches other side, it is promoted to a better piece...
                            elif isinstance(startSquare.piece, Pawn) and (
                                    (currentPlayer == 1 and endSquare.row == 7) or
                                    (currentPlayer == 2 and endSquare.row == 0)):
                                endSquare.piece = startSquare.piece
                                startSquare.piece = None
                                print("Your pawn has been promoted!")
                                print("Take your pick:")
                                print("1 for queen")
                                print("2 for bishop")
                                print("3 for knight")
                                print("4 for rook")
                                while True:
                                    promotion = input(">")
                                    if "1" <= promotion <= "4":
                                        promotion = int(promotion)
                                        if promotion == 1:
                                            endSquare.piece = Queen(
                                                currentPlayer)
                                        elif promotion == 2:
                                            endSquare.piece = Bishop(
                                                currentPlayer)
                                        elif promotion == 3:
                                            endSquare.piece = Knight(
                                                currentPlayer)
                                        elif promotion == 4:
                                            endSquare.piece = Rook(
                                                currentPlayer)
                                        else:
                                            promotion = None
                                    else:
                                        promotion = None
                                    if promotion is None:
                                        print(
                                            "Invalid selection, please try again")
                                    else:
                                        break

                            # "Move" code for the rest of the pieces and the normal king moves, too
                            else:
                                savedPiece = endSquare.piece
                                endSquare.piece = startSquare.piece
                                if isinstance(endSquare.piece, King):
                                    king.location = endSquare
                                startSquare.piece = None
                                if board.check(currentPlayer):
                                    if inCheck:
                                        print(
                                            "Your move keeps you in check, please try again")
                                    else:
                                        print(
                                            "Your move places you in check, please try again")
                                    startSquare.piece = endSquare.piece
                                    if isinstance(endSquare.piece, King):
                                        king.location = startSquare
                                    endSquare.piece = savedPiece
                                else:
                                    # Track the first move of each piece since some
                                    # moves require that no previous moves have been made
                                    endSquare.piece.moved = True
                                    break
                        else:
                            print("Illegal move, please try again")

        if onlineGame:  # ToDo: reconsider position for this
            network.send(startCode + endCode)

    # Re-draw board: after (i.e.: before and after)
    clear()
    if onlineGame:
        board.draw(player)
    else:
        board.draw(currentPlayer)

    # Check for game ending possibilities for offense immediately after move
    if not onlineGame or (onlineGame and currentPlayer == player):
        if board.check(currentOtherPlayer):
            if board.checkmate(currentOtherPlayer):
                print("Checkmate!  You win!")
                gameOn = False
            else:
                print("You put your opponent in check!")
        elif board.stalemate(currentOtherPlayer):
            print("No legal moves left!  Stalemate")
            gameOn = False

    # Necessary so offline games can see the previous message
    if not onlineGame:
        input("<PRESS ENTER TO CONTINUE>")

    # Employ move that is transmitted from opponent
    if onlineGame and gameOn and (currentPlayer == player or firstMove):
        firstMove = False
        print("Wait for opponent to finish their move...")
        theirMove = network.receive()
        startLocation = decode(theirMove[0:2])
        startSquare = board.getSquare(startLocation[0], startLocation[1])
        endLocation = decode(theirMove[2:4])
        endSquare = board.getSquare(endLocation[0], endLocation[1])
        endSquare.piece = startSquare.piece
        startSquare.piece = None
        # if castling...
        # ToDo: GENERIC CASTLING FUNCTION
        # ToDo: need logic for pawn promotion
        if isinstance(endSquare.piece, King) and \
                abs(endSquare.column - startSquare.column) == 2:
            rookRow = endSquare.row
            if endSquare.column < 4:
                rookColumn = 0
                rookColumnNew = 3
            else:
                rookColumn = 7
                rookColumnNew = 5
            rookSquare = board.getSquare(rookRow, rookColumn)
            rookSquareNew = board.getSquare(rookRow, rookColumnNew)
            rookSquareNew.piece = rookSquare.piece
            rookSquare.piece = None

    # Switch players and loop
    if currentPlayer == 1:
        currentPlayer = 2
        currentOtherPlayer = 1
    else:
        currentPlayer = 1
        currentOtherPlayer = 2
