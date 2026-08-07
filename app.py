#!/usr/bin/python3

#################################################################
#                                                               #
#      Unicode Chess, written by Robert Rutherford in 2021      #
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

# If the app needs to be served from a /chess/ subdirectory, the old redirect can
# be restored by uncommenting the block below and updating the hosting setup so
# requests to /chess/ are routed to this app.
# from flask import redirect
# @app.route("/chess/", methods=["GET"])
# def chess_subdirectory_redirect():
#     return redirect("/chess/")
# To reinstate the subdirectory behavior:
# 1. Ensure the web server or deployment target serves this app under /chess/.
# 2. Update any links and static asset URLs to include the /chess/ prefix.
# 3. Uncomment the import and route above, then restart the application.

def handle_form_submission():
	parameters = request.form
	recaptcha_passed = False
	recaptcha_response = parameters.get('g-recaptcha-response')
	try:
		recaptcha_secret = reCAPTCHAv3.secret_key
		response = requests.post(f'https://www.google.com/recaptcha/api/siteverify?secret={recaptcha_secret}&response={recaptcha_response}').json()
		recaptcha_passed = response.get('success')
	except Exception as e:
		print(f"failed to get reCaptcha: {e}")

	if not recaptcha_passed:
		return "Are you human!?"

	formtype = request.form.get("form_type")

	if formtype == "setup":
		new_game = request.form.get("is_game_new") == "1"
		if new_game:
			player_choice_str = request.form.get("player_choice")
			if player_choice_str is None:
				return "Missing player choice.", 400
			try:
				player_choice = int(player_choice_str)
			except ValueError:
				return "Invalid player choice.", 400
			return remoteSetup(True, 0, player_choice)
		else:
			game_code_str = request.form.get("saved_game_code")
			if game_code_str is None:
				return "Missing game code.", 400
			try:
				game_code = int(game_code_str)
			except ValueError:
				return "Invalid game code.", 400
			return remoteSetup(False, game_code, 0)

	elif formtype == "move":
		game_code_str = request.form.get("game_code")
		player_code_str = request.form.get("player_code")
		if game_code_str is None or player_code_str is None:
			return "Missing game or player code.", 400
		try:
			game_code = int(game_code_str)
			player_code = int(player_code_str)
		except ValueError:
			return "Invalid game or player code.", 400
		game = load_game(str(game_code) + ".chess")
		return game.chess_page(player_code)

	else:
		return "Unknown form type.", 400

@app.route("/", methods=["GET", "POST"])
def gameplay():
	if request.method == "POST":
		return handle_form_submission()
	if request.method == "GET":
		game_code = request.args.get("game")
		player_code = request.args.get("player")
		if ((game_code is not None) and (player_code is not None)):
			game = load_game(game_code + ".chess")
			return game.chess_page(int(player_code))
	return homeScreen()
