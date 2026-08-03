import base64
import hashlib
import http.server
import json
import secrets
import threading
import urllib.parse
import webbrowser

from urllib.request import Request, urlopen


# ============================================================
# Portable Spotify Player
# M005.1C - Spotify Token Manager
# ============================================================

CLIENT_ID = "254edd10f6b342cebacd982c4ba2685f"

REDIRECT_URI = "http://127.0.0.1:8888/callback"
PORT = 8888

TOKEN_FILE = "token.json"

SCOPES = "user-read-currently-playing"


# ============================================================
# Token Storage
# ============================================================

def save_token(token_data):
    with open(TOKEN_FILE, "w") as file:
        json.dump(token_data, file, indent=4)

    print("Token saved locally.")


def load_token():
    try:
        with open(TOKEN_FILE, "r") as file:
            return json.load(file)

    except FileNotFoundError:
        return None


# ============================================================
# PKCE
# ============================================================

def generate_pkce():

    code_verifier = (
        base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        )
        .rstrip(b"=")
        .decode("utf-8")
    )

    code_challenge = (
        base64.urlsafe_b64encode(
            hashlib.sha256(
                code_verifier.encode("utf-8")
            ).digest()
        )
        .rstrip(b"=")
        .decode("utf-8")
    )

    return code_verifier, code_challenge


# ============================================================
# Spotify OAuth
# ============================================================

authorization_code = None
callback_error = None
oauth_state = None


class CallbackHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        global authorization_code
        global callback_error

        parsed = urllib.parse.urlparse(self.path)

        params = urllib.parse.parse_qs(
            parsed.query
        )

        received_state = params.get(
            "state",
            [None]
        )[0]

        if received_state != oauth_state:

            callback_error = "State mismatch."

            self.send_response(400)
            self.end_headers()

            self.wfile.write(
                b"State mismatch."
            )

            return

        if "error" in params:

            callback_error = params["error"][0]

            self.send_response(400)
            self.end_headers()

            self.wfile.write(
                f"Spotify authorization failed: {callback_error}".encode()
            )

            return

        authorization_code = params.get(
            "code",
            [None]
        )[0]

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html"
        )

        self.end_headers()

        self.wfile.write(
            b"""
            <html>
            <body>
                <h2>Spotify authorization successful!</h2>
                <p>You can close this browser window.</p>
            </body>
            </html>
            """
        )

    def log_message(self, format, *args):
        pass


def run_oauth():

    global oauth_state

    code_verifier, code_challenge = generate_pkce()

    oauth_state = secrets.token_urlsafe(32)

    server = http.server.HTTPServer(
        ("127.0.0.1", PORT),
        CallbackHandler
    )

    server_thread = threading.Thread(
        target=server.handle_request
    )

    server_thread.start()

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": oauth_state,
        "code_challenge_method": "S256",
        "code_challenge": code_challenge,
    }

    authorization_url = (
        "https://accounts.spotify.com/authorize?"
        + urllib.parse.urlencode(params)
    )

    print()
    print("Opening Spotify authorization...")

    webbrowser.open(
        authorization_url
    )

    print("Waiting for Spotify callback...")

    server_thread.join()

    server.server_close()

    if callback_error:

        raise RuntimeError(
            f"Authorization failed: {callback_error}"
        )

    if not authorization_code:

        raise RuntimeError(
            "No authorization code received."
        )

    print("Authorization code received.")

    # --------------------------------------------------------
    # Exchange authorization code for token
    # --------------------------------------------------------

    token_data = urllib.parse.urlencode({

        "client_id": CLIENT_ID,

        "grant_type":
            "authorization_code",

        "code":
            authorization_code,

        "redirect_uri":
            REDIRECT_URI,

        "code_verifier":
            code_verifier,

    }).encode("utf-8")

    request = Request(

        "https://accounts.spotify.com/api/token",

        data=token_data,

        headers={
            "Content-Type":
                "application/x-www-form-urlencoded"
        },

        method="POST"
    )

    with urlopen(request) as response:

        token_response = json.loads(
            response.read().decode("utf-8")
        )

    return token_response


# ============================================================
# Refresh Access Token
# ============================================================

def refresh_access_token(refresh_token):

    token_data = urllib.parse.urlencode({

        "client_id":
            CLIENT_ID,

        "grant_type":
            "refresh_token",

        "refresh_token":
            refresh_token,

    }).encode("utf-8")

    request = Request(

        "https://accounts.spotify.com/api/token",

        data=token_data,

        headers={
            "Content-Type":
                "application/x-www-form-urlencoded"
        },

        method="POST"
    )

    with urlopen(request) as response:

        return json.loads(
            response.read().decode("utf-8")
        )


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("==============================================")
    print("Portable Spotify Player")
    print("M005.1C - Spotify Token Manager")
    print("==============================================")

    token_data = load_token()

    # --------------------------------------------------------
    # Existing token
    # --------------------------------------------------------

    if token_data:

        print()
        print("Existing token found.")

        refresh_token = token_data.get(
            "refresh_token"
        )

        if not refresh_token:

            print(
                "No refresh token found."
            )

            print(
                "Starting OAuth..."
            )

            token_data = run_oauth()

        else:

            print(
                "Refreshing access token..."
            )

            try:

                refreshed_token = (
                    refresh_access_token(
                        refresh_token
                    )
                )

                token_data.update(
                    refreshed_token
                )

                # Spotify may not return a new
                # refresh token every time.
                if "refresh_token" not in refreshed_token:

                    token_data[
                        "refresh_token"
                    ] = refresh_token

                print(
                    "Access token refreshed successfully."
                )

            except Exception as error:

                print(
                    "Token refresh failed:"
                )

                print(error)

                print(
                    "Starting OAuth again..."
                )

                token_data = run_oauth()

    # --------------------------------------------------------
    # No token
    # --------------------------------------------------------

    else:

        print()
        print(
            "No token found."
        )

        print(
            "Starting Spotify OAuth..."
        )

        token_data = run_oauth()

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_token(token_data)

    print()
    print("==============================================")
    print("TOKEN MANAGER READY")
    print("==============================================")

    print(
        "Access token: RECEIVED"
    )

    if token_data.get("refresh_token"):

        print(
            "Refresh token: RECEIVED"
        )

    print(
        "Expires in:",
        token_data.get("expires_in"),
        "seconds"
    )

    print()
    print(
        "Your tokens remain local and are ignored by Git."
    )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()