#!/usr/bin/python3

#################################################################
#                                                               #
#       ASCII-Chess, written by Robert Rutherford in 2021       #
#                                                               #
#################################################################


import os
from os.path import exists
from urllib.parse import quote, unquote
import jsonpickle
from random import randint
from hashlib import shake_128
from chess import Chess
from flask import request, url_for
from board import Square
from recaptchav3 import reCAPTCHAv3


class Game(object):

    gamecode: int
    filename: str
    chess_game: Chess
    player1code: int
    player2code: int
    hostPlayer: int
    guestPlayer: int

    def __init__(self, gamecode: int):

        if gamecode is None:
            gamecode = randint(1000,9999)
            self.gamecode = gamecode
            gameHash = shake_128()
            gameHash.update(gamecode.to_bytes(4, 'big'))
            gameHash = gameHash.digest(4)
            self.player1code = int(str(gameHash.hex())[0:4], 16)
            self.player2code = int(str(gameHash.hex())[4:8], 16)
            self.chess_game = Chess()
        self.filename = str(gamecode) + '.chess'

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
                self.chess_game.promotePawn(promotion_choice)

                # Check to see if this promotion just ended the game and process move
                if self.chess_game.gameOn:
                    self.chess_game.switchPlayers()
                    awaiting_turn = "1"
                    self.save_game(self.filename, self.chess_game)
                else:
                    disabled_input = " disabled"  # End game
                    disabled_submit = " disabled"

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

        # Check for end of game, save game, and display appropriate board to user
        game_status = self.chess_game.gameStatus(player)
        if not self.chess_game.gameOn:
            disabled_input = " disabled"
            disabled_submit = " disabled"
        save_game(self)
        output = self.chess_game.drawBoard(player)
        if player == self.chess_game.currentPlayer:
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
            <link rel="shortcut icon" href="{favicon_code}">
            <style>
                input, div {{ display: block; }}
                .board {{ white-space: pre; font-family: monospace, monospace; font-size: small; margin: 0px; }}
                label, h3 {{ font-weight: bold; }}
                .error {{ color: red; }}
                .gameStatus {{ color: green; }}
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
            <script src="https://www.google.com/recaptcha/api.js?render={reCAPTCHA_site_key}"></script>
            <script>
                grecaptcha.ready(function () {{
                    grecaptcha.execute('{reCAPTCHA_site_key}', {{action: 'validate_captcha'}}).then(function (token) {{
                        console.info("got token: " + token);
                        document.getElementById('g-recaptcha-response').value = token;
                    }});
                }});
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
                <input type="hidden" id="g-recaptcha-response" name="g-recaptcha-response">
                <input type="hidden" name="action" value="validate_captcha">
                <input type="submit" {disabled_submit} />
            </form>
       </body>
    </html>
        '''.format(game_code=self.gamecode, player_code=player_code, awaiting_turn=awaiting_turn, output=output, error=error,
                   pawn_label_hidden=pawn_label_hidden, pawn_dialog_hidden=pawn_dialog_hidden, promotion=promotion,
                   game_status=game_status, disabled_input1=disabled_input, disabled_input2=disabled_input,
                   disabled_submit=disabled_submit, favicon_code=url_for('static', filename='favicon.ico'),
                   header_text=header_text, reCAPTCHA_site_key=reCAPTCHAv3.site_key)


def save_game(game: Game):
    cpickle = jsonpickle.encode(game)
    cstring = quote(cpickle)
    game.filename = str(game.gamecode) + ".chess"
    if not os.path.exists("games"):
        os.mkdir("games")
    cfile = open("games/" + game.filename, "w")
    cfile.write(cstring)
    cfile.close()


# Load a game from the server
def load_game(filename: str) -> Game:
    if exists("games/" + filename):
        cfile = open("games/" + filename, "r")
        cstring = cfile.readline()
        cpickle = unquote(cstring)
        game = jsonpickle.decode(cpickle)
        cfile.close()
        return game
    else:
        raise Exception("No saved game found")
