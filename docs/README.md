# Unicode Chess
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

This is a **Python** chess game run using [Flask](https://flask.palletsprojects.com/en/2.2.x/) that allows two people to play a game across the internet on their own respective browsers.  It is called "Unicode Chess" because the pieces are unicode chess characters.  Unicode characters replaced the ASCII characters of earlier versions of the game that were called "ASCII Chess."

![screenshot](screenshot.png)

Go to [https://unicode-chess.vercel.app/](https://unicode-chess.vercel.app/) to play a game!

## Table of Contents

- [Security](#security)
- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Security

Other than the built-in security features offered by **Flask**, the communications over **Vercel** are secured with SSL/TLS and HTTPS.

## Background

This game originated as a simple **Python** program.  Communication capabilities were added to it.  Then, in an effort to demonstrate the game, it became necessary to play it through a web browser.  Thereafter, the program was re-written using **Flask** to make that possible.

## Install

1. Install Python 3, pip, and venv if they are not already available.

On Ubuntu or Debian:

```
sudo apt-get install -y python3 python3-pip python3-venv
```

Use the equivalent package manager or installer for your operating system if you are not on Ubuntu or Debian.

2. Clone the project and change into the repository directory:

```
git clone https://github.com/rbrutherford3/Unicode-Chess.git
cd Unicode-Chess
```

3. Create and activate a virtual environment:

```
python3 -m venv .venv
source .venv/bin/activate
```

4. Install Python dependencies from the project requirements file:

```
pip3 install -r requirements.txt
```

5. Create Google reCAPTCHAv3 site key and secret keys, making sure your reCAPTCHA configuration allows `localhost` and `127.0.0.1`.

6. Set those environment variables before running the app:

```
export RECAPTCHA_SITE_KEY="your-site-key"
export RECAPTCHA_SECRET_KEY="your-secret-key"
```

Note that these variables are required whether you are running locally or in production.

If you are deploying to Vercel, set the same values in your Vercel project environment variables so the app can access them at runtime.

7. Optional: enable Flask debug mode before running:

```
export FLASK_DEBUG=1
```

8. Run the program:

```
python3 -m flask run
```

(you can also add `--debug` at the end of this command instead of setting `FLASK_DEBUG=1` in step 6)

You should see something like the following:

```
...
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
...
```

This means you can now go to `localhost:5000` or `127.0.0.1:5000` in your browser to use the program. To start or join a game successfully, the reCAPTCHA keys from step 5 must be valid for that local host.

9. Optional: when you are done using the app, deactivate the virtual environment:
```
deactivate
```

### Notes:

This project is also compatible with [Vercel](https://vercel.com/), and the same requirements file is used for its Python dependencies.

## Usage

For the rules of chess, here is an article for beginners: https://www.chess.com/learn-how-to-play-chess

To play, you must find someone to play with and each player must be reading from the same server (i.e.: [https://unicode-chess.vercel.app/](https://unicode-chess.vercel.app/)).  Each will visit the site and one will commence the game.  A player code and a game code are provided to each player.  As the names suggest, the player code is unique to the player and the game code is unique to the game.  The person who starts the game will somehow have to give the other play the game code.  Once the other player enters the game code, the game begins.

The players commence by typing in location codes in "algebraic notation" (a1 or e7, for example). One location code for the starting position and one for the destination.  The page will accept input until a move is submitted, at which point the other person will be allowed to make a move.  The game is saved on the server until one of the players wins or a stalemate occurs.  Games can be bookmarked for later play.

### IMPORTANT:

Note that because **Vercel** is a serverless system that there are occasional deletions that cause games to be lost. This current setup is meant to be a demonstration only. It is possible that it will move to a database-driven system where games will be saved indefinitely, but until then, expect that game progress will be randomly lost.

## Contributing

Contributions are welcome, including any feedback.

## License

[MIT © Robert Rutherford](../LICENSE)
