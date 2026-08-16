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

#### 1. Install Python 3, pip, and venv if they are not already available

On Ubuntu or Debian:

```
sudo apt-get install -y python3 python3-pip python3-venv
```

Use the equivalent package manager or installer for your operating system if you are not on Ubuntu or Debian.

#### 2. Clone the project and change into the repository directory

```
git clone https://github.com/rbrutherford3/Unicode-Chess.git
cd Unicode-Chess
```

#### 3. Create and activate a virtual environment

```
python3 -m venv .venv
source .venv/bin/activate
```

#### 4. Install Python dependencies from the project requirements file

```
pip3 install -r requirements.txt
```

#### 5. Create a Cloudflare Turnstile widget and site key/secret, making sure the widget's allowed domains include `localhost` and `127.0.0.1`

#### 6. Create a [neon](https://neon.com/) account and get a connection URL like the own shown below in step 7

#### 7. Set the Turnstile variables and a PostgreSQL connection string before running the app:

```
export TURNSTILE_SITE_KEY="your-turnstile-site-key"
export TURNSTILE_SECRET="your-turnstile-secret"
export TURNSTILE_HOSTNAMES="localhost,127.0.0.1"
export DATABASE_URL="postgresql://username:password@host/database?sslmode=require"
```

Note that these variables are required whether you are running locally or in production.

If you deploy on Vercel, add `TURNSTILE_SECRET`, `TURNSTILE_SITE_KEY`, and `TURNSTILE_HOSTNAMES` to the project environment. Set `TURNSTILE_HOSTNAMES` to the production frontend hostnames only, for example `unicode-chess.vercel.app`; do not include local development hosts in production.

#### 8. Optional: enable Flask debug mode before running:

```
export FLASK_DEBUG=1
```

#### 9. Run the program:

```
python3 -m flask run
```

(you can also add `--debug` at the end of this command instead of setting `FLASK_DEBUG=1` in step 8)

You should see something like the following:

```
...
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
...
```

This means you can now go to `localhost:5000` or `127.0.0.1:5000` in your browser to use the program. To start or join a game successfully, the Turnstile keys from step 5 must be valid for that local host.

#### 10. Optional: when you are done using the app, deactivate the virtual environment:
```
deactivate
```

### Notes:

This project is also compatible with [Vercel](https://vercel.com/), and the same requirements file is used for its Python dependencies.

## Usage

For the rules of chess, here is an article for beginners: https://www.chess.com/learn-how-to-play-chess

To play, you must find someone to play with and each player must be reading from the same server (i.e.: [https://unicode-chess.vercel.app/](https://unicode-chess.vercel.app/)).  Each will visit the site and one will commence the game.  A player code and a game code are provided to each player.  As the names suggest, the player code is unique to the player and the game code is unique to the game.  The person who starts the game will somehow have to give the other play the game code.  Once the other player enters the game code, the game begins.

The players commence by typing in location codes in "algebraic notation" (a1 or e7, for example). One location code for the starting position and one for the destination.  The page will accept input until a move is submitted, at which point the other person will be allowed to make a move.  The game is saved until one of the players wins or a stalemate occurs.  Games can be bookmarked for later play, or a player can use their game code and player code to re-enter the game from the site.

## Contributing

Contributions are welcome, including any feedback.

## License

[MIT © Robert Rutherford](../LICENSE)
