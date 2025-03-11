#!/usr/bin/python3

#################################################################
#                                                               #
#      Unicode Chess, written by Robert Rutherford in 2021      #
#                                                               #
#################################################################

from flask import request, url_for
from random import randint
from os import system
from hashlib import shake_128
from game import Game, save_game, load_game
from recaptchav3 import reCAPTCHAv3

# Initiate the game between two people
# (decide who is white or black, provide game and player codes)
def remoteSetup(new_game: bool, game_code: int, player_choice: int):
    if new_game:
        game = Game(None)
        game_code = game.gamecode
        if (player_choice == 3):
            player_choice = randint(1,2)
        if ((player_choice == 1) or (player_choice == 2)):
            game.setHostPlayer(player_choice)
            player_code = game.getPlayerCode(player_choice)
        else:
            raise Exception("Player choice must be either '1' or '2'")
        save_game(game)
    else:
        if (game_code is not None and game_code > 0):
            game = load_game(str(game_code) + '.chess')
            player = game.getGuestPlayer()
            player_code = int(game.getPlayerCode(player))
            save_game(game)
        else:
            raise Exception("Need game code")
    return '''
<!DOCTYPE html>
<html>
    <head>
        <title>Chess game setup</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="shortcut icon" href="{favicon_code}">
        <style>
            input, div {{ display: block; }}
            .board {{ white-space: pre; font-family: monospace, monospace; font-size: small; margin: 10px; }}
            label {{ font-weight: bold; font-size: 12pt; }}
            .error {{ color: red; }}
            .gameStatus {{ color: green; }}
        </style>
    </head>
    <body>
        <h1>Give your game code</h1>
        Use this code to give to your opponent so you may find each other
        <h2>{game_code}</h2>
        <h1>Get your secret code!</h1>
        Use this code to access your game at any time (or simply bookmark the \
            next page).  If you give this code to your opponent then they will \
            be able to move your pieces, so be careful)
        <h2>{player_code}</h2>
        <a href="?game={game}&player={player}" style="text-decoration: none;"><input type="button" value="Start game" /></a>
    </body>
</html>
            '''.format(game_code=game_code,player_code=player_code,game=game_code,player=player_code,favicon_code=url_for('static', filename='favicon.ico'))

def homeScreen():
    return '''
<!DOCTYPE html>
<html>
    <head>
        <title>Chess game setup</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="shortcut icon" href="{favicon_code}">
        <style>
            input, div {{ display: block; }}
            .board {{ white-space: pre; font-family: monospace, monospace; font-size: small; margin: 10px; }}
            label {{ font-weight: bold; font-size: 12pt; }}
            .error {{ color: red; }}
            .gameStatus {{ color: green; }}
        </style>
        <script>
            function showSavedInput() {{
                document.getElementById("saved_game_code").style.display = "initial";
                document.getElementById("saved_game_code_label").style.display = "initial";
                return 0;
            }}
            function hideSavedInput() {{
                document.getElementById("saved_game_code").style.display = "none";
                document.getElementById("saved_game_code_label").style.display = "none";
                return 0;
            }}
            function showPlayerInput() {{
                document.getElementById("player_choice_1").style.display = "initial";
                document.getElementById("player_choice_1_label").style.display = "initial";
                document.getElementById("player_choice_2").style.display = "initial";
                document.getElementById("player_choice_2_label").style.display = "initial";
                document.getElementById("player_choice_3").style.display = "initial";
                document.getElementById("player_choice_3_label").style.display = "initial";
                return 0;
            }}
            function hidePlayerInput() {{
                document.getElementById("player_choice_1").style.display = "none";
                document.getElementById("player_choice_1_label").style.display = "none";
                document.getElementById("player_choice_2").style.display = "none";
                document.getElementById("player_choice_2_label").style.display = "none";
                document.getElementById("player_choice_3").style.display = "none";
                document.getElementById("player_choice_3_label").style.display = "none";
                return 0;
            }}
            function showSubmit() {{
                document.getElementById("submit").style.display = "initial";
                return 0;
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
    <body>
        <form name="game_setup" method="post">
            <input type="hidden" name="form_type" value="setup" />
            <h1>Chess game setup</h1>
            <p>
                <input type="radio" name="is_game_new" id="start_new" value="1" onclick="hideSavedInput(); showPlayerInput();">
                <label for="start_new">Start a new game</label>
                <input type="radio" name="is_game_new" id="resume_old" value="0" onclick="hidePlayerInput(); showSavedInput();">
                <label for="resume_old">Join or resume a game</label>
            </p>
            <p style="display: block;">
                <label for="saved_game_code" id="saved_game_code_label" onclick="showSubmit();" style="display: none;">Enter code for saved game:</label>
                <input type="text" name="saved_game_code" id="saved_game_code" onclick="showSubmit();" style="display: none;" />
                <input type="radio" name="player_choice" id="player_choice_1" onclick="showSubmit();" value=1 style="display: none;" />
                <label for="player_choice_1" id="player_choice_1_label" onclick="showSubmit();" style="display: none;" />Player 1 (white)</label>
                <input type="radio" name="player_choice" id="player_choice_2" onclick="showSubmit();" value=2 style="display: none;" />
                <label for="player_choice_2" id="player_choice_2_label" onclick="showSubmit();" style="display: none;" />Player 2 (black)</label>
                <input type="radio" name="player_choice" id="player_choice_3" onclick="showSubmit();" value=3 style="display: none;" />
                <label for="player_choice_3" id="player_choice_3_label" onclick="showSubmit();" style="display: none;" />Random</label>
            </p>
            <p>
                <input type="hidden" id="g-recaptcha-response" name="g-recaptcha-response">
                <input type="hidden" name="action" value="validate_captcha">
                <input type="submit" id="submit" value="Submit" style="display: none;" />
            </p>
        </form>
    <body>
</html>
'''.format(favicon_code=url_for('static', filename='favicon.ico'), reCAPTCHA_site_key=reCAPTCHAv3.site_key)
