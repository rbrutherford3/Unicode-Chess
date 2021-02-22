#################################################################
#                                                               #
#       ASCII-Chess, written by Robert Rutherford in 2021       #
#                                                               #
#################################################################

# Todo: Stalemate check

from abc import ABC
from typing import Optional


# Abstract class to model chess pieces by providing necessary attributes
class Piece(ABC):
    name: str  # name of piece, i.e.: 'king'
    symbol: str  # shorthand of piece for display on board
    value: int  # algebraic value (not used)
    player: int  # belongs to player 1 or 2
    moves: frozenset  # all the legal moves for the piece, as vectors
    scalable: bool  # can piece move freely along a given path (i.e.: queen)?
    specialMoves: bool  # does this piece have moves outside of the norm (i.e.: castling)
    moved: bool = False  # monitor if the piece has moved at all (for castling only)

    # start with player number
    def __init__(self, thisPlayer: int):
        self.player: int = thisPlayer


# Pawn class (note that all pawn moves are atypical, to a strange degree, so no 'typical' moves are listed)
class Pawn(Piece):
    name = "pawn"
    symbol = "p"
    value = 1
    moves = None  # all pawn movements are affected by surrounding pieces
    scalable = False
    specialMoves = True


# Knight class
class Knight(Piece):
    name = "knight"
    symbol = "N"
    value = 3
    moves = frozenset([
        (2, 1),
        (2, -1),
        (-2, 1),
        (-2, -1),
        (1, 2),
        (-1, 2),
        (-1, -2),
        (1, -2),
    ])
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


# Rook class (note that it is not marked as special because it can't initiate castling, only follows it)
class Rook(Piece):
    name = "rook"
    symbol = "R"
    value = 5
    moves = frozenset([(1, 0), (-1, 0), (0, 1), (0, -1)])
    scalable = True
    specialMoves = True


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
    name = "king"
    symbol = "K"
    value = None
    moves = frozenset([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1),
                       (-1, -1), (-1, 1)])
    scalable = False
    specialMoves = True


# Class that represents one square on a board (note that indexing in Python is from 0, so translation is required)
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
def decode(code: str):		# -> Optional[tuple[int, int]]:
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
class Board(object):		# Square objects are assigned a location on a
    grid: list # [list[Square]] # two-dimensional gridded 'board'
    numRows: int = 8
    numColumns: int = 8

    opponent = opponent  # stealing function for getting the opposite player

    # Begin by initiating grid
    def __init__(self):
        self.grid = [[
            Square(gridRow, gridColumn)
            for gridColumn in range(self.numColumns)
        ] for gridRow in range(self.numRows)]

    # This method sets up each individual piece on the 'grid'
    def setup(self):

        [
            self.grid[1][column].setPiece(Pawn(1))
            for column in range(self.numColumns)
        ]
        [
            self.grid[6][column].setPiece(Pawn(2))
            for column in range(self.numColumns)
        ]
        [self.grid[0][column].setPiece(Rook(1)) for column in [0, 7]]
        [self.grid[7][column].setPiece(Rook(2)) for column in [0, 7]]
        [self.grid[0][column].setPiece(Knight(1)) for column in [1, 6]]
        [self.grid[7][column].setPiece(Knight(2)) for column in [1, 6]]
        [self.grid[0][column].setPiece(Bishop(1)) for column in [2, 5]]
        [self.grid[7][column].setPiece(Bishop(2)) for column in [2, 5]]
        self.grid[0][3].setPiece(Queen(1))
        self.grid[7][3].setPiece(Queen(2))
        self.grid[0][4].setPiece(King(1))
        self.grid[7][4].setPiece(King(2))

    # Draw the board onto the screen with unicode ASCII characters (old school, yes)
    def draw(self):

        print("")
        print(
            "        a       b       c       d       e       f       g       h"
        )
        print(
            "    -----------------------------------------------------------------"
        )
        print(
            "    |       |///////|       |///////|       |///////|       |///////|"
        )
        print(" 8  |  " + str(self.grid[7][0]) + "  |//" +
              str(self.grid[7][1]) + "//|  " + str(self.grid[7][2]) + "  |//" +
              str(self.grid[7][3]) + "//|  " + str(self.grid[7][4]) + "  |//" +
              str(self.grid[7][5]) + "//|  " + str(self.grid[7][6]) + "  |//" +
              str(self.grid[7][7]) + "//|  8")
        print(
            "    |       |///////|       |///////|       |///////|       |///////|"
        )
        print(
            "    -----------------------------------------------------------------"
        )
        print(
            "    |///////|       |///////|       |///////|       |///////|       |"
        )
        print(" 7  |//" + str(self.grid[6][0]) + "//|  " +
              str(self.grid[6][1]) + "  |//" + str(self.grid[6][2]) + "//|  " +
              str(self.grid[6][3]) + "  |//" + str(self.grid[6][4]) + "//|  " +
              str(self.grid[6][5]) + "  |//" + str(self.grid[6][6]) + "//|  " +
              str(self.grid[6][7]) + "  |  7")
        print(
            "    |///////|       |///////|       |///////|       |///////|       |"
        )
        print(
            "    -----------------------------------------------------------------"
        )
        print(
            "    |       |///////|       |///////|       |///////|       |///////|"
        )
        print(" 6  |  " + str(self.grid[5][0]) + "  |//" +
              str(self.grid[5][1]) + "//|  " + str(self.grid[5][2]) + "  |//" +
              str(self.grid[5][3]) + "//|  " + str(self.grid[5][4]) + "  |//" +
              str(self.grid[5][5]) + "//|  " + str(self.grid[5][6]) + "  |//" +
              str(self.grid[5][7]) + "//|  6")
        print(
            "    |       |///////|       |///////|       |///////|       |///////|"
        )
        print(
            "    -----------------------------------------------------------------"
        )
        print(
            "    |///////|       |///////|       |///////|       |///////|       |"
        )
        print(" 5  |//" + str(self.grid[4][0]) + "//|  " +
              str(self.grid[4][1]) + "  |//" + str(self.grid[4][2]) + "//|  " +
              str(self.grid[4][3]) + "  |//" + str(self.grid[4][4]) + "//|  " +
              str(self.grid[4][5]) + "  |//" + str(self.grid[4][6]) + "//|  " +
              str(self.grid[4][7]) + "  |  5")
        print(
            "    |///////|       |///////|       |///////|       |///////|       |"
        )
        print(
            "    -----------------------------------------------------------------"
        )
        print(
            "    |       |///////|       |///////|       |///////|       |///////|"
        )
        print(" 4  |  " + str(self.grid[3][0]) + "  |//" +
              str(self.grid[3][1]) + "//|  " + str(self.grid[3][2]) + "  |//" +
              str(self.grid[3][3]) + "//|  " + str(self.grid[3][4]) + "  |//" +
              str(self.grid[3][5]) + "//|  " + str(self.grid[3][6]) + "  |//" +
              str(self.grid[3][7]) + "//|  4")
        print(
            "    |       |///////|       |///////|       |///////|       |///////|"
        )
        print(
            "    -----------------------------------------------------------------"
        )
        print(
            "    |///////|       |///////|       |///////|       |///////|       |"
        )
        print(" 3  |//" + str(self.grid[2][0]) + "//|  " +
              str(self.grid[2][1]) + "  |//" + str(self.grid[2][2]) + "//|  " +
              str(self.grid[2][3]) + "  |//" + str(self.grid[2][4]) + "//|  " +
              str(self.grid[2][5]) + "  |//" + str(self.grid[2][6]) + "//|  " +
              str(self.grid[2][7]) + "  |  3")
        print(
            "    |///////|       |///////|       |///////|       |///////|       |"
        )
        print(
            "    -----------------------------------------------------------------"
        )
        print(
            "    |       |///////|       |///////|       |///////|       |///////|"
        )
        print(" 2  |  " + str(self.grid[1][0]) + "  |//" +
              str(self.grid[1][1]) + "//|  " + str(self.grid[1][2]) + "  |//" +
              str(self.grid[1][3]) + "//|  " + str(self.grid[1][4]) + "  |//" +
              str(self.grid[1][5]) + "//|  " + str(self.grid[1][6]) + "  |//" +
              str(self.grid[1][7]) + "//|  2")
        print(
            "    |       |///////|       |///////|       |///////|       |///////|"
        )
        print(
            "    -----------------------------------------------------------------"
        )
        print(
            "    |///////|       |///////|       |///////|       |///////|       |"
        )
        print(" 1  |//" + str(self.grid[0][0]) + "//|  " +
              str(self.grid[0][1]) + "  |//" + str(self.grid[0][2]) + "//|  " +
              str(self.grid[0][3]) + "  |//" + str(self.grid[0][4]) + "//|  " +
              str(self.grid[0][5]) + "  |//" + str(self.grid[0][6]) + "//|  " +
              str(self.grid[0][7]) + "  |  1")
        print(
            "    |///////|       |///////|       |///////|       |///////|       |"
        )
        print(
            "    -----------------------------------------------------------------"
        )
        print(
            "        a       b       c       d       e       f       g       h"
        )
        print("")

    # Reference a particular square on the grid
    def getSquare(self, row: int, column: int) -> Square:
        if row in range(self.numRows) and column in range(self.numColumns):
            return self.grid[row][column]
        else:
            return None #raise ValueError("Chess board is 8x8, please using 0-7 indices")

    # Get all possible moves (even if capturing an piece)
    # For this to work, the piece is "walked" along the board until it runs out or hits an opponent or neighbor
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
                                    if (
                                            not start.piece.scalable
                                    ):  # Stop if limited to move one square only
                                        break
                                elif (
                                        square.piece.player == otherPlayer
                                ):  # Stop if opponent is encountered (capture)
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
        if square.piece.name == "pawn":
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
                if forwardTwo is None:
                    return moves
                else:
                    if forwardTwo.piece is None:
                        moves = moves.union([forwardTwo])
                        return moves
        else:
            raise ValueError("Square does not contain a pawn")

    # Other than the typical moves, a king has castling opportunities
    # There are two castling directions: King-side (4 squares wide) and Queen-side (5 squares wide)
    # This method adds those moves only if they are eligible (not in check, path clear, etc)
    def getKingMoves(self, kingSquare: Square) -> frozenset:
        moves = frozenset()
        if kingSquare.piece.name == "king":
            if kingSquare.piece.moved:
                return frozenset()
            row = kingSquare.row
            kingColumn = kingSquare.column
            rookColumn = 7
            firstMove = self.getSquare(row, kingColumn + 1)
            secondMove = self.getSquare(row, kingColumn + 2)
            rookSquare = self.getSquare(row, rookColumn)
            if not (rookSquare is None or rookSquare.piece is None or
                    rookSquare.piece.name != "rook" or rookSquare.piece.moved
                    or firstMove is None or firstMove.piece is not None
                    or secondMove is None or secondMove.piece is not None):
                moves = moves.union([secondMove])
            rookColumn = 0
            firstMove = self.getSquare(row, kingColumn - 1)
            secondMove = self.getSquare(row, kingColumn - 2)
            thirdMove = self.getSquare(row, kingColumn - 3)
            rookSquare = self.getSquare(row, rookColumn)
            if not (rookSquare is None or rookSquare.piece is None or
                    rookSquare.piece.name != "rook" or rookSquare.piece.moved
                    or firstMove is None or firstMove.piece is not None
                    or secondMove is None or secondMove.piece is not None
                    or thirdMove is None or thirdMove.piece is not None):
                moves = moves.union([secondMove])
        return moves

    # Combines all possible moves from one player to see where the opponent's king would be in check or not
    def checkZone(self, aggressor: int) -> frozenset:
        checkZone = frozenset()
        for checkRow in self.grid:
            for checkSquare in checkRow:
                if checkSquare.piece is not None:
                    if checkSquare.piece.player == aggressor:
                        # Again, pawns are unique in their movements, so they are added separately
                        if checkSquare.piece.name == "pawn":
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
    def check(self, square: Square, player: int) -> bool:
        return square in self.checkZone(opponent(player))

    # Brute force loop through the entire grid to find the king
    # Due to how the data has been set up, there aren't any ways to quickly refer to a specific piece
    def findKing(self, player: int) -> Square:
        for row in self.grid:
            for square in row:
                if square.piece is not None:
                    if square.piece.player == player:
                        if square.piece.name == "king":
                            return square

    # For all moves on one side, move each piece once to see if the king would still be in check (checkmate)
    # The pieces are walked back from the check to preserve the layout
    # Castling is not considered due to check restrictions:
    # "cannot castle into, out of, or through check"
    def checkmate(self, forPlayer: int) -> bool:
        checkmated = True
        for row in self.grid:
            square: Square
            for square in row:
                if square.piece is not None and square.piece.player == forPlayer:
                    if square.piece.name == "pawn":
                        testMoves = self.getPawnMoves(square)
                    else:
                        testMoves = self.getMoves(square)
                    if testMoves is not None:
                        move: Square
                        for move in testMoves:
                            pieceSaved = False
                            savedPiece = None
                            if move.piece is not None:
                                pieceSaved = True
                                savedPiece = move.piece
                            move.piece = square.piece
                            square.piece = None
                            if not self.check(self.findKing(forPlayer),
                                              forPlayer):
                                checkmated = False
                            square.piece = move.piece
                            if pieceSaved:
                                move.piece = savedPiece
                            else:
                                move.piece = None
        return checkmated

    # If no moves are possible for a given side, then there is a stalemate
    def stalemate(self, player: int) -> bool:
        stalemate = False
        for row in self.grid:
            for square in row:
                if square is not None:
                    if square.piece is not None:
                        if square.piece.player == player:
                            moves: frozenset = frozenset()
                            if square.piece.name == "king":
                                moves = moves.union(
                                    self.getMoves(square).union(
                                        self.getKingMoves(square)))
                            elif square.piece.name == "pawn":
                                moves = moves.union(self.getPawnMoves(square))
                            else:
                                moves = moves.union(self.getMoves(square))
                            if len(moves) == 0:
                                stalemate = True
        return stalemate


### SET UP USER INTERFACE FOR GAMEPLAY ###

board = Board()  # Need an instance of the board to refer to it's methods
board.setup()
gameOn = True
player = 1
otherPlayer = 2

# Keep looping through turns until the game ends
while gameOn:

    board.draw()  # Redraw the board after each turn

    # Check to see if there was a game ending situation
    inCheck = False
    if board.check(board.findKing(player), player):
        if board.checkmate(player):
            print("Checkmate!  You lose!")
            break
        else:
            inCheck = True
            print("You are in check!")

    # Cycle through user input for moves (square for beginning, square for ending)
    while True:

        # Loop until beginning square is established
        while True:
            print("Player #", player)
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
                        if startSquare.piece.player == player:
                            break
                        else:
                            print("Please select a player on your own side")

        # Gather moves possibilities for special pieces and all other pieces, too
        if startSquare.piece.name == "pawn":
            moves = board.getPawnMoves(startSquare)
        elif startSquare.piece.name == "king":
            moves = board.getMoves(startSquare).union(
                board.getKingMoves(startSquare))
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
                if moves is None:  # this line doesn't seem to work well
                    print(
                        "No moves available for this piece, please try again")
                else:
                    if endSquare in moves:

                        # if castling...
                        if (startSquare.piece.name == "king"
                                and startSquare.row == endSquare.row
                                and abs(endSquare.column - startSquare.column)
                                == 2):
                            row = endSquare.row

                            # look for checking along castle (must not enter or leave check)
                            if endSquare.column > startSquare.column:
                                startColumnKing = 4
                                endColumnRook = 5
                                endColumnKing = 6
                                extraColumn = None
                                startColumnRook = 7
                            else:
                                startColumnKing = 4
                                endColumnRook = 3
                                endColumnKing = 2
                                extraColumn = 1
                                startColumnRook = 0
                            startSquareKing = startSquare
                            startSquareRook = board.getSquare(
                                row, startColumnRook)
                            endSquareKing = endSquare
                            endSquareRook = board.getSquare(row, endColumnRook)

                            # Make sure path is clear for castling
                            clearPath = False
                            if (endSquareKing.piece is None
                                    and endSquareRook.piece is None):
                                if extraColumn is not None:
                                    extraSquare = board.getSquare(
                                        row, extraColumn)
                                    if extraSquare.piece is None:
                                        clearPath = True
                                else:
                                    clearPath = True

                            # Make sure king never encounters check
                            clearCheck = True
                            if (board.check(startSquareKing, player)
                                    or board.check(endSquareRook, player)
                                    or board.check(endSquareKing, player)):
                                clearCheck = False

                            # Make sure king and rook have never been moved
                            firstMoves = True
                            # noinspection PyUnresolvedReferences
                            if (startSquareRook.piece.moved
                                    or startSquareKing.piece.moved):
                                firstMoves = False

                            # move pieces if everything looks good
                            if clearPath and clearCheck and firstMoves:
                                endSquareKing.piece = startSquareKing.piece
                                startSquareKing.piece = None
                                endSquareRook.piece = startSquareRook.piece
                                startSquareRook.piece = None
                                break

                            # Explain why the castle move was rejected:
                            if not firstMoves:
                                print(
                                    "The king and/or the rook must have moved yet"
                                )
                            elif not clearPath:
                                print(
                                    "Your path must be clear of any pieces in order to castle"
                                )
                            elif not clearCheck:
                                print(
                                    "You may not castle from, through, or into check"
                                )
                        # Todo: may need to add other pawn responses (don't think so, though)

                        # If pawn reaches other side, it is promoted to a better piece...
                        elif startSquare.piece.name == "pawn" and (
                            (player == 1 and endSquare.row == 7) or
                            (player == 2 and endSquare.row == 0)):
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
                                        endSquare.piece = Queen(player)
                                    elif promotion == 2:
                                        endSquare.piece = Bishop(player)
                                    elif promotion == 3:
                                        endSquare.piece = Knight(player)
                                    elif promotion == 4:
                                        endSquare.piece = Rook(player)
                                    else:
                                        promotion = None
                                else:
                                    promotion = None
                                if promotion is None:
                                    print(
                                        "Invalid selection, please try again")
                                else:
                                    break

                        # Move code for the rest of the pieces and the normal king moves, too
                        else:
                            savedPiece = endSquare.piece
                            endSquare.piece = startSquare.piece
                            startSquare.piece = None
                            if board.check(board.findKing(player), player):
                                if inCheck:
                                    print(
                                        "Your move places you in check, please try again"
                                    )
                                else:
                                    print("Your move keeps you in check")
                                startSquare.piece = endSquare.piece
                                endSquare.piece = savedPiece
                            else:
                                break
                    else:
                        print("Illegal move, please try again")

    # Track the first move of each piece since some moves require that no previous moves have been made
    endSquare.piece.moved = True

    # Check for game ending situations
    if board.check(board.findKing(otherPlayer), otherPlayer):
        if board.checkmate(otherPlayer):
            print("Checkmate!  You win!")
        else:
            print("You placed your opponent in check!")

    # Switch players
    if player == 1:
        player = 2
        otherPlayer = 1
    else:
        player = 1
        otherPlayer = 2
