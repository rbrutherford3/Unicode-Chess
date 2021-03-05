#################################################################
#                                                               #
#       ASCII-Chess, written by Robert Rutherford in 2021       #
#                                                               #
#################################################################


from piece import *


# Yield the opposite player
def opponent(player):
    if player == 1:
        return 2
    elif player == 2:
        return 1
    else:
        raise ValueError("Players are either 1 or 2")


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

    # Need quick access to the king for each side to speed up program
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

        if player == 1:
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
        elif player == 2:
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
            return None    # raise ValueError("Please use 0-7 indices")

    # Get all possible moves (even if capturing a piece)
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

    # Pawns are unique in only moving one direction, capturing pieces at an angle, and more.
    # As a result, they have their own method for movement
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
