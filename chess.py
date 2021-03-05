#################################################################
#                                                               #
#       ASCII-Chess, written by Robert Rutherford in 2021       #
#                                                               #
#################################################################
# ToDo: fix up dialog between player and network @ beginning
# ToDo: Make back and forth packages more reliable (Maybe serialize board object)
# ToDo: Keep-alive signal?
# ToDo: comments, functions, possibly add a class or two (TDB)


from board import *
from network import *
from os import system, name


# define our clear function (https://www.geeksforgeeks.org/clear-screen-python/)
def clear():
    # for windows
    if name == "nt":
        _ = system("cls")

        # for mac and linux(here, os.name is 'posix')
    else:
        _ = system("clear")


# Converts user shorthand for squares into row and column tuple for use in program
def decode(code: str):  # -> Optional[tuple[int, int]]:
    letters: list[str] = ["a", "b", "c", "d", "e", "f", "g", "h"]
    if len(code) == 2:
        char1: str = code[0]
        char2: str = code[1]
        if "a" <= char1.lower() <= "h" and "1" <= char2 <= "8":
            column: int = letters.index(char1.lower())
            rowNum: int = int(char2) - 1
            return rowNum, column
        else:
            return None
    else:
        return None


[network, onlineGame, player] = accessNetwork()

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

    # Re-draw the board (in the current orientation)
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
        startSquare = None
        endSquare = None
        startCode = None
        endCode = None
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
