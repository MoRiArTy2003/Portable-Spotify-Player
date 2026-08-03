import base64
import hashlib
import http.server
import json
import secrets
import threading
import urllib
import webbrowser
from urllib.request  import Request, urlopen

#===============================================
# Portable Spotify Player
# Mission M005.1A - Spotify OAuth + PKCE
#===============================================

CLIENT_ID = "254edd10f6b342cebacd982c4ba2685f"

REDIRECT_URI = "http://127.0.0.1:8888/callback"
PORT = 8888

SCOPES = "user-read-currently-playing"

#==============================================
# PKCE
#==============================================

code_verifier = (
  base64.urlsafe_b64encode(secrets.token_bytes(32))
  .rstrip(b"=")
  .decode("utf-8")
)

code_challenge = base64.urlsafe_b64encode(
  hashlib.sha256(code_verifier.encode("utf-8")).digest()).rstrip(b"=").decode("utf-8")

state = secrets.token_urlsafe(32)

#================================================
# Callback Handling
#================================================

authorization_code = None
callback_error = None

class CallbackHandler(http.server.BaseHTTPRequestHandler):
  
  def do_GET(self):
    global authorization_code, callback_error
    
    parsed = urllib.parse.urlparse(self.path)
    params = urllib.parse.parse_qs(parsed.query)
    
    if params.get("state", [None])[0] != state:
      callback_error = "State mismatch."
      self.send_response(400)
      self.end_headers()
      self.wfile.write(b"State mismatch.")
      return
    
    if "error" in params:
      callback_error = params["error"][0]
      self.send_response(400)
      self.end_headers()
      self.wfile.write(
        f"Spotify authorization failed: {callback_error}".encode()
      )
      return
    
    authorization_code = params.get("code",[None])[0]
    
    self.send_response(200)
    self.send_header("Content-Type", "text/html")
    self.end_headers()
    
    self.wfile.write(
      b"""
      <html>
      <body>
          <h2>Spotify authorization sucessful!<h2>
          <p>You can close this browser window<p>
      </body>
      </html>
      """
    )
    
    def log_messsage(self, format, *args):
      pass
    
#==============================================
# Start Local callback Server
#==============================================

server = http.server.HTTPServer(
  ("127.0.0.1", PORT),
  CallbackHandler
)

server_thread = threading.Thread(
  target=server.handle_request
)

server_thread.start()


#==============================================
# Build Spotify authorization URL
#==============================================

params = {
  "client_id": CLIENT_ID,
  "response_type": "code",
  "redirect_uri": REDIRECT_URI,
  "scope": SCOPES,
  "state": state,
  "code_challenge_method": "S256",
  "code_challenge": code_challenge,
}

authorization_url = (
  "https://accounts.spotify.com/authorize?"
  + urllib.parse.urlencode(params)
)

print()
print("==============================================")
print("Portable Spotify Player")
print("M005.1A - Spotify OAuth + PKCE")
print("==============================================")
print()
print("Opening Spotify authorization.....")
print()

webbrowser.open(authorization_url)

print("Waiting for Spotify callback...")


#==============================================
# Wait for Callback
#==============================================

server_thread.join()

server.server_close()

if callback_error:
  print()
  print("Authorization Failed")
  print(callback_error)
  raise SystemExit(1)

if not authorization_code:
  print()
  print("No authorization code received.")
  raise SystemExit(1)

print()
print("Authorization code Received!")
print("Exchanging code for access token....")


def save_token(token_data):
  with open("token.json", "w") as file:
    json.dump(token_data, file, indent=4)
    
    print("Token saved locally to token.json")

#==============================================
# Exchange code for token
#==============================================

token_data = urllib.parse.urlencode({
  "client_id": CLIENT_ID,
  "grant_type": "authorization_code",
  "code": authorization_code,
  "redirect_uri": REDIRECT_URI,
  "code_verifier": code_verifier,
}).encode("utf-8")

request = Request(
  "https://accounts.spotify.com/api/token",
  data=token_data,
  headers={
    "Content-Type": "application/x-www-form-urlencoded"
  },
  method="POST"
)

try:
  
  with urlopen(request) as response:
    
    token_response = json.loads(
      response.read().decode("utf-8")
    )
    save_token(token_response)
    
except Exception as error:
  print()
  print("Token exchange failed:")
  print(error)
  raise SystemExit(1)

#==============================================
# Success
#==============================================

print()
print("==============================================")
print("SUCCESS!")
print("==============================================")

print()
print("Token type:", token_response.get("token_type"))
print("Expires in:", token_response.get("expires_in"), "seconds")
print("Scope", token_response.get("scope"))

if "access_token" in token_response:
  print("Access token: RECEIVED")
  
if "refresh_token" in token_response:
  print("Refresh token: RECEIVED")
  
print()
print("DO NOT share the access or refresh token.")
print()