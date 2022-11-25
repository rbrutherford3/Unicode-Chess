#!/usr/bin/python3

#################################################################
#                                                               #
#       ASCII-Chess, written by Robert Rutherford in 2021       #
#                                                               #
#################################################################

from flask import Flask, request
from remote_setup import homeScreen, remoteSetup
from game import load_game
from recaptchav3 import reCAPTCHAv3
import requests

# Initiate flask program
app = Flask(__name__)
app.config["DEBUG"] = False
app.secret_key = "awf98gjhgb"

# Route incoming http requests to the appropriate function
@app.route("/chess/", methods=["GET", "POST"])
def gameplay():
	if request:
		if (request.method == "POST"):
			parameters = request.form
			recaptcha_passed = False
			recaptcha_response = parameters.get('g-recaptcha-response')
			try:
				recaptcha_secret = reCAPTCHAv3.secret_key
				response = requests.post(f'https://www.google.com/recaptcha/api/siteverify?secret={recaptcha_secret}&response={recaptcha_response}').json()
				recaptcha_passed = response.get('success')
			except Exception as e:
				print(f"failed to get reCaptcha: {e}")
			if recaptcha_passed:
				formtype = request.form.get("form_type")
				if formtype == "setup":
					new_game = request.form.get("is_game_new") == "1"
					if new_game:
						player_choice = int(request.form.get("player_choice"))
						return remoteSetup(True, 0, player_choice)
					else:
						game_code = int(request.form.get("saved_game_code"))
						return remoteSetup(False, game_code, 0)
				elif formtype == "move":
					game_code = int(request.form.get("game_code"))
					game = load_game(str(game_code) + ".chess")
					player_code = int(request.form.get("player_code"))
					return game.chess_page(int(player_code))
			else:
				return "Are you human!?"
		elif (request.method == "GET"):
			game_code = request.args.get("game")
			player_code = request.args.get("player")
			if ((game_code is not None) and (player_code is not None)):
				game = load_game(game_code + ".chess")
				return game.chess_page(int(player_code))
	return homeScreen()
