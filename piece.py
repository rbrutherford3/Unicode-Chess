#################################################################
#                                                               #
#       ASCII-Chess, written by Robert Rutherford in 2021       #
#                                                               #
#################################################################


from abc import ABC


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
