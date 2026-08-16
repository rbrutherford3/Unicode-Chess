#!/usr/bin/python3

#################################################################
#                                                               #
#      Unicode Chess, written by Robert Rutherford in 2021      #
#                                                               #
#################################################################

from flask import request, url_for
from random import randint
from game import Game
from game_store import create_game, load_game, save_game
from turnstile import Turnstile

# Initiate the game between two people
# (decide who is white or black, provide game and player codes)
def remoteSetup(new_game: bool, game_code: int, player_choice: int):
    if new_game:
        if (player_choice == 3):
            player_choice = randint(1,2)
        if ((player_choice == 1) or (player_choice == 2)):
            for _ in range(10):
                game = Game(None)
                game.setHostPlayer(player_choice)
                player_code = game.getPlayerCode(player_choice)
                if create_game(game):
                    break
            else:
                raise Exception("Unable to allocate a unique game code")
            game_code = game.gamecode
        else:
            raise Exception("Player choice must be either '1' or '2'")
    else:
        if (game_code is not None and game_code > 0):
            game = load_game(game_code)
            # The guest's player code can only be revealed once; after that, require it be entered.
            if game.guestCodeClaimed:
                return promptPlayerCode(game_code)
            game.guestCodeClaimed = True
            save_game(game)
            player = game.getGuestPlayer()
            player_code = int(game.getPlayerCode(player))
        else:
            raise Exception("Need game code")
    return '''
<!DOCTYPE html>
<html>
    <head>
        <title>Chess game setup</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="icon" type="image/png" sizes="32x32" href="{favicon_32}">
        <link rel="icon" type="image/png" sizes="16x16" href="{favicon_16}">
        <link rel="apple-touch-icon" sizes="180x180" href="{apple_touch_icon}">
        <link rel="manifest" href="{manifest}">
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
            '''.format(game_code=game_code,player_code=player_code,game=game_code,player=player_code,
                       favicon_32=url_for('static', filename='favicon-32x32.png'),
                       favicon_16=url_for('static', filename='favicon-16x16.png'),
                       apple_touch_icon=url_for('static', filename='apple-touch-icon.png'),
                       manifest=url_for('static', filename='site.webmanifest'))

# Ask a returning player for their player code once the game/guest code has already been claimed
def promptPlayerCode(game_code: int, error: str = "") -> str:
    return '''
<!DOCTYPE html>
<html>
    <head>
        <title>Chess game setup</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="icon" type="image/png" sizes="32x32" href="{favicon_32}">
        <link rel="icon" type="image/png" sizes="16x16" href="{favicon_16}">
        <link rel="apple-touch-icon" sizes="180x180" href="{apple_touch_icon}">
        <link rel="manifest" href="{manifest}">
        <style>
            input, div {{ display: block; }}
            label {{ font-weight: bold; font-size: 12pt; }}
            .error {{ color: red; }}
        </style>
    </head>
    <body>
        <form method="post" action="/">
            <input type="hidden" name="form_type" value="join_verify" />
            <input type="hidden" name="game_code" value="{game_code}" />
            <h1>Enter your player code</h1>
            This game code has already been claimed. Enter your player code to continue.
            <h3 class="error">{error}</h3>
            <label for="player_code">Player code:</label>
            <input type="text" name="player_code" id="player_code" autofocus />
            <input type="submit" value="Submit" />
        </form>
    </body>
</html>
            '''.format(game_code=game_code, error=error,
                       favicon_32=url_for('static', filename='favicon-32x32.png'),
                       favicon_16=url_for('static', filename='favicon-16x16.png'),
                       apple_touch_icon=url_for('static', filename='apple-touch-icon.png'),
                       manifest=url_for('static', filename='site.webmanifest'))

def homeScreen():
    return '''
<!DOCTYPE html>
<html>
    <head>
        <title>Chess game setup</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="icon" type="image/png" sizes="32x32" href="{favicon_32}">
        <link rel="icon" type="image/png" sizes="16x16" href="{favicon_16}">
        <link rel="apple-touch-icon" sizes="180x180" href="{apple_touch_icon}">
        <link rel="manifest" href="{manifest}">
        <style>
            input, label {{ display: inline-block; }}
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
            let formReady = false;
            let turnstileDone = false;
            function maybeShowSubmit() {{
                if (formReady && turnstileDone) {{
                    document.getElementById("submit").style.display = "initial";
                }}
                return 0;
            }}
            function markFormReady() {{
                formReady = true;
                maybeShowSubmit();
                return 0;
            }}
            function onTurnstileSuccess() {{
                turnstileDone = true;
                maybeShowSubmit();
                return 0;
            }}
            function blockSubmitUntilTurnstile(event) {{
                if (!turnstileDone) {{
                    event.preventDefault();
                }}
                return 0;
            }}
        </script>
        <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
    </head>
    <body>
        <form name="game_setup" method="post" action="/" onsubmit="blockSubmitUntilTurnstile(event);">
            <input type="hidden" name="form_type" value="setup" />
            <h1>Chess game setup</h1>
            <div>
                <div>
                    <input type="radio" name="is_game_new" id="start_new" value="1" onclick="hideSavedInput(); showPlayerInput();">
                    <label for="start_new">Start a new game</label>
		</div>
                <div>
                    <input type="radio" name="is_game_new" id="resume_old" value="0" onclick="hidePlayerInput(); showSavedInput();">
                    <label for="resume_old">Join or resume a game</label>
                </div>
            </div>
            <br>
            <div>
                <div>
                    <label for="saved_game_code" id="saved_game_code_label" onclick="markFormReady();" style="display: none;">Enter code for saved game:</label>
                    <input type="text" name="saved_game_code" id="saved_game_code" onclick="markFormReady();" style="display: none;" />
                </div>
                <div>
                    <input type="radio" name="player_choice" id="player_choice_1" onclick="markFormReady();" value=1 style="display: none;" />
                    <label for="player_choice_1" id="player_choice_1_label" onclick="markFormReady();" style="display: none;" />Player 1 (white)</label>
                </div>
                <div>
                    <input type="radio" name="player_choice" id="player_choice_2" onclick="markFormReady();" value=2 style="display: none;" />
                    <label for="player_choice_2" id="player_choice_2_label" onclick="markFormReady();" style="display: none;" />Player 2 (black)</label>
                </div>
                <div>
                    <input type="radio" name="player_choice" id="player_choice_3" onclick="markFormReady();" value=3 style="display: none;" />
                    <label for="player_choice_3" id="player_choice_3_label" onclick="markFormReady();" style="display: none;" />Random</label>
                </div>
            </div>
            <br>
            <div>
                <div class="cf-turnstile" data-sitekey="{turnstile_site_key}" data-action="setup" data-callback="onTurnstileSuccess"></div>
                <input type="submit" id="submit" value="Submit" style="display: none;" />
            </div>
        </form>
    <body>
</html>
'''.format(favicon_32=url_for('static', filename='favicon-32x32.png'),
           favicon_16=url_for('static', filename='favicon-16x16.png'),
           apple_touch_icon=url_for('static', filename='apple-touch-icon.png'),
           manifest=url_for('static', filename='site.webmanifest'),
           turnstile_site_key=Turnstile.site_key)
