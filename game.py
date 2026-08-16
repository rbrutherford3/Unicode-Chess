#!/usr/bin/python3

#################################################################
#                                                               #
#      Unicode Chess, written by Robert Rutherford in 2021      #
#                                                               #
#################################################################


import secrets
from chess import Chess
from flask import request, url_for
from board import Square
from pieces import (
    BlackBishop,
    BlackKing,
    BlackKnight,
    BlackPawn,
    BlackQueen,
    BlackRook,
    WhiteBishop,
    WhiteKing,
    WhiteKnight,
    WhitePawn,
    WhiteQueen,
    WhiteRook,
)
from game_store import load_game, save_game


class Game(object):

    gamecode: int
    chess_game: Chess
    player1code: int
    player2code: int
    hostPlayer: int
    guestPlayer: int
    version: int
    guestCodeClaimed: bool

    def __init__(self, gamecode: int):
        if gamecode is None:
            self.gamecode = secrets.randbelow(900000) + 100000
            self.player1code = secrets.randbelow(9000000000000000) + 1000000000000000
            self.player2code = secrets.randbelow(9000000000000000) + 1000000000000000
            self.chess_game = Chess()
            self.version = 0
            self.guestCodeClaimed = False

    @classmethod
    def from_state(cls, state: dict, version: int) -> "Game":
        game = cls.__new__(cls)
        game.gamecode = state["game_code"]
        game.player1code = state["player_1_code"]
        game.player2code = state["player_2_code"]
        game.hostPlayer = state["host_player"]
        game.guestCodeClaimed = state.get("guest_code_claimed", False)
        game.version = version
        game.chess_game = Chess()
        board = game.chess_game.board
        for row, serialized_row in enumerate(state["board"]):
            for column, serialized_piece in enumerate(serialized_row):
                square = board.getSquare(row, column)
                square.piece = game._piece_from_state(serialized_piece)
                if isinstance(square.piece, (WhiteKing, BlackKing)):
                    if square.piece.player == 1:
                        board.king1 = square.piece
                    else:
                        board.king2 = square.piece
                    square.piece.location = square
        game.chess_game.currentPlayer = state["current_player"]
        game.chess_game.gameOn = state["game_on"]
        pending_promotion = state.get("pending_promotion")
        if pending_promotion is not None:
            game.chess_game.endSquare = board.getSquare(*pending_promotion)
        return game

    def to_state(self) -> dict:
        board = self.chess_game.board
        pending_promotion = None
        end_square = getattr(self.chess_game, "endSquare", None)
        if end_square is not None and self.chess_game.promotePawnCheck():
            pending_promotion = [end_square.row, end_square.column]
        return {
            "game_code": self.gamecode,
            "player_1_code": self.player1code,
            "player_2_code": self.player2code,
            "host_player": self.hostPlayer,
            "guest_code_claimed": self.guestCodeClaimed,
            "current_player": self.chess_game.currentPlayer,
            "game_on": self.chess_game.gameOn,
            "pending_promotion": pending_promotion,
            "board": [
                [self._piece_to_state(square.piece) for square in row]
                for row in board.grid
            ],
        }

    @staticmethod
    def _piece_to_state(piece):
        if piece is None:
            return None
        state = {"type": piece.name, "player": piece.player, "moved": piece.moved}
        if isinstance(piece, (WhitePawn, BlackPawn)):
            state["en_passant"] = piece.enPassant
        return state

    @staticmethod
    def _piece_from_state(state):
        if state is None:
            return None
        piece_classes = {
            ("pawn", 1): WhitePawn, ("pawn", 2): BlackPawn,
            ("knight", 1): WhiteKnight, ("knight", 2): BlackKnight,
            ("bishop", 1): WhiteBishop, ("bishop", 2): BlackBishop,
            ("rook", 1): WhiteRook, ("rook", 2): BlackRook,
            ("queen", 1): WhiteQueen, ("queen", 2): BlackQueen,
            ("king", 1): WhiteKing, ("king", 2): BlackKing,
        }
        try:
            piece = piece_classes[(state["type"], state["player"])]()
        except KeyError as error:
            raise ValueError("Saved game contains an invalid piece") from error
        piece.moved = state["moved"]
        if isinstance(piece, (WhitePawn, BlackPawn)):
            piece.enPassant = state.get("en_passant", False)
        return piece

    def setHostPlayer(self, player: int):
        self.hostPlayer = player

    def getGuestPlayer(self) -> int:
        return Square.opponent(self.hostPlayer)

    def getPlayerCode(self, player: int) -> int:
        if player == 1:
            return self.player1code
        elif player == 2:
            return self.player2code
        else:
            raise Exception("Player must be 1 or 2")

    # Main gameplay function (heart of program)
    def chess_page(self, player_code: int) -> str:
        # Save game as a file on the server (as a JSON pickle)

        # Set all initial values to their default
        error = ""
        disabled_input = ""
        disabled_submit = ""
        pawn_label_hidden = " style=\"display: none;\""
        pawn_dialog_hidden = " hidden"
        promotion = "0"
        awaiting_turn = "0"
        should_save = False

        if self.player1code == player_code:
            player = 1
        elif self.player2code == player_code:
            player = 2
        else:
            raise Exception("No valid player code was submitted")

        # If it's my turn...
        if player == self.chess_game.currentPlayer:

            # Check to see if pawn reached the other side in the last move
            # and change the piece to the player's choice
            if request.form.get("promotion") == "1":
                promotion_choice = request.form.get("promotion_pieces")
                error = self.chess_game.promotePawn(promotion_choice)
                if not error:
                    self.chess_game.switchPlayers()
                    awaiting_turn = "1"
                    should_save = True
                else:
                    promotion = 1
                    pawn_label_hidden = ""
                    pawn_dialog_hidden = ""
                    disabled_input = " disabled"

            # If this was a normal move...
            elif ((request.form.get("next_move_start") is not None) and (
                    request.form.get("next_move_start") is not None)):
                next_move_start = request.form.get("next_move_start")
                next_move_end = request.form.get("next_move_end")
                error = self.chess_game.movePiece(next_move_start, next_move_end, player)

                # If there were no problems with the move...
                if len(error) == 0:

                    # If pawn made it to the last row, then choose a piece to promote it to
                    promote_pawn_check = self.chess_game.promotePawnCheck()
                    if promote_pawn_check:
                        promotion = 1
                        pawn_label_hidden = ""
                        pawn_dialog_hidden = ""
                        disabled_input = " disabled"

                    # End move if not a promotion
                    else:
                        self.chess_game.switchPlayers()
                    should_save = True

        # Check for end of game, save game, and display appropriate board to user
        game_was_on = self.chess_game.gameOn
        game_status = self.chess_game.gameStatus(player)
        if not self.chess_game.gameOn:
            disabled_input = " disabled"
            disabled_submit = " disabled"
        if should_save or game_was_on != self.chess_game.gameOn:
            save_game(self)
        output = self.chess_game.drawBoard(player)
        if not self.chess_game.gameOn:
            header_text = "Game over!"
        elif player == self.chess_game.currentPlayer:
            header_text = "Your turn!"
        else:
            header_text = "Awaiting opponent..."
            awaiting_turn = "1"
            disabled_input = " disabled"
            disabled_submit = " disabled"
        return '''
    <!DOCTYPE html>
    <html>
        <head>
            <title>Chess game in progress</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="icon" type="image/png" sizes="32x32" href="{favicon_32}">
            <link rel="icon" type="image/png" sizes="16x16" href="{favicon_16}">
            <link rel="apple-touch-icon" sizes="180x180" href="{apple_touch_icon}">
            <link rel="manifest" href="{manifest}">
            <style>
                input, div {{ display: block; }}
                .board {{ white-space: pre; font-family: monospace, monospace; font-size: small; margin: 0px; }}
                label, h3 {{ font-weight: bold; }}
                .error {{ color: red; }}
                .gameStatus {{ color: green; }}
                .white {{ display: inline-block; width: 25px; height: 25px; line-height: 25px; text-align: center; font-size: 20px; background-color: white; }}
                .black {{ display: inline-block; width: 25px; height: 25px; line-height: 25px; text-align: center; font-size: 20px; background-color: darkgray; }}
                .toplabel {{ border-bottom: 1px solid black; }}
                .bottomlabel {{ border-top: 1px solid black; }}
                .leftlabel {{ border-right: 1px solid black; }}
                .rightlabel {{ border-left: 1px solid black; }}
            </style>
            <script>
                function sleep(ms) {{
                    return new Promise(resolve => setTimeout(resolve, ms));
                }}

                async function awaitingTurn() {{
                    if (document.getElementById("awaiting_turn").value == "1")
                    {{
                        await sleep(5000);
                        var game_code = document.getElementById("game_code").value;
                        var player_code = document.getElementById("player_code").value;
                        window.location.href = window.location.pathname + "?game=" + game_code + "&player=" + player_code;
                    }}
                }}
            </script>
        </head>
        <body onload = "awaitingTurn();">
            <form id="move_form" method="post" action=".">
                <h3>{header_text}</h3>
                <input type="hidden" name="form_type" id="form_type" value="move" />
                <input type="hidden" name="game_code" id="game_code" value={game_code} />
                <input type="hidden" name="player_code" id="player_code" value={player_code} />
                <input type="hidden" name="awaiting_turn" id="awaiting_turn" value={awaiting_turn} />
                <div class="board">{output}</div>
                <h3 class="error">{error}</h3>
                <label for="promotion_pieces" id="promotion_pieces_label"{pawn_label_hidden}>Pick a piece to promote your \
                pawn to!</label>
                <select name="promotion_pieces" id="promotion_pieces"{pawn_dialog_hidden}>
                    <option value="1">Queen</option>
                    <option value="2">Bishop</option>
                    <option value="3">Knight</option>
                    <option value="4">Rook</option>
                </select>
                <input type="hidden" name="promotion" value={promotion} />
                <h3 class="gameStatus">{game_status}</h3>
                <label for="next_move_start">Select piece to move:</label>
                <input type="text" id="next_move_start" name="next_move_start" style="margin: 10px;" {disabled_input2} \
                autofocus/>
                <label for="next_move_end">Select square to move to:</label>
                <input type="text" id="next_move_end" name="next_move_end" style="margin: 10px;" {disabled_input1} />
                <input type="submit" {disabled_submit} />
            </form>
       </body>
    </html>
        '''.format(game_code=self.gamecode, player_code=player_code, awaiting_turn=awaiting_turn, output=output, error=error,
                   pawn_label_hidden=pawn_label_hidden, pawn_dialog_hidden=pawn_dialog_hidden, promotion=promotion,
                   game_status=game_status, disabled_input1=disabled_input, disabled_input2=disabled_input,
                   disabled_submit=disabled_submit, favicon_32=url_for('static', filename='favicon-32x32.png'),
                   favicon_16=url_for('static', filename='favicon-16x16.png'),
                   apple_touch_icon=url_for('static', filename='apple-touch-icon.png'),
                   manifest=url_for('static', filename='site.webmanifest'),
                   header_text=header_text)



