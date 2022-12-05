#!/usr/bin/python3

#################################################################
#                                                               #
#      Unicode Chess, written by Robert Rutherford in 2021      #
#                                                               #
#################################################################

from piecetypes import Pawn, Knight, Bishop, Rook, Queen, King

class WhitePawn(Pawn):
    def __init__(self):
        super().__init__(1)
    symbol = "&#9817;"

class BlackPawn(Pawn):
    def __init__(self):
        super().__init__(2)
    symbol = "&#9823;"

class WhiteKnight(Knight):
    def __init__(self):
        super().__init__(1)
    symbol = "&#9816;"
    
class BlackKnight(Knight):
    def __init__(self):
        super().__init__(2)
    symbol = "&#9822;"

class WhiteBishop(Bishop):
    def __init__(self):
        super().__init__(1)
    symbol = "&#9815;"

class BlackBishop(Bishop):
    def __init__(self):
        super().__init__(2)
    symbol = "&#9821;"

class WhiteRook(Rook):
    def __init__(self):
        super().__init__(1)
    symbol = "&#9814;"

class BlackRook(Rook):
    def __init__(self):
        super().__init__(2)
    symbol = "&#9820;"

class WhiteQueen(Queen):
    def __init__(self):
        super().__init__(1)
    symbol = "&#9813;"

class BlackQueen(Queen):
    def __init__(self):
        super().__init__(2)
    symbol = "&#9819;"

class WhiteKing(King):
    def __init__(self):
        super().__init__(1)
    symbol = "&#9812;"

class BlackKing(King):
    def __init__(self):
        super().__init__(2)
    symbol = "&#9818;"