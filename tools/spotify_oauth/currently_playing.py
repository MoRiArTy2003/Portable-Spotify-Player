import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError


TOKEN_FILE = "token.json"

CURRENTLY_PLAYING_URL = (
    "https://api.spotify.com/v1/me/player/currently-playing"
)


def load_token():
    with open(TOKEN_FILE, "r") as file:
        return json.load(file)


def get_currently_playing(access_token):
    request = Request(
        CURRENTLY_PLAYING_URL,
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        method="GET"
    )

    try:
        with urlopen(request) as response:
            return response.status, response.read().decode("utf-8")

    except HTTPError as error:
        return error.code, error.read().decode("utf-8")


def main():

    print()
    print("==============================================")
    print("Portable Spotify Player")
    print("M005.2 - Currently Playing")
    print("==============================================")

    # Load token
    try:
        token_data = load_token()
    except FileNotFoundError:
        print()
        print("token.json not found.")
        print("Run spotify_oauth.py first.")
        return

    access_token = token_data.get("access_token")

    if not access_token:
        print()
        print("No access token found.")
        print("Run spotify_oauth.py first.")
        return

    # Ask Spotify
    print()
    print("Asking Spotify what is playing...")

    status_code, response_text = get_currently_playing(
        access_token
    )

    print()
    print("HTTP Status:", status_code)

    # Nothing playing
    if status_code == 204:
        print()
        print("Nothing is currently playing.")
        return

    # API error
    if status_code != 200:
        print()
        print("Spotify API request failed.")
        print(response_text)
        return

    # Parse JSON
    data = json.loads(response_text)

    if not data.get("item"):
        print()
        print("No currently playing item.")
        return

    item = data["item"]

    # Track
    track_name = item.get(
        "name",
        "Unknown"
    )

    # Artists
    artists = item.get(
        "artists",
        []
    )

    artist_names = ", ".join(
        artist.get("name", "Unknown")
        for artist in artists
    )

    # Album
    album = item.get(
        "album",
        {}
    )

    album_name = album.get(
        "name",
        "Unknown"
    )

    # Playback
    is_playing = data.get(
        "is_playing",
        False
    )

    progress_ms = data.get(
        "progress_ms"
    )

    duration_ms = item.get(
        "duration_ms"
    )

    # Display
    print()
    print("🎵 CURRENTLY PLAYING")
    print("--------------------------------")

    print("Track   :", track_name)
    print("Artist  :", artist_names)
    print("Album   :", album_name)

    print(
        "Status  :",
        "PLAYING" if is_playing else "PAUSED"
    )

    if progress_ms is not None:
        print(
            "Progress:",
            progress_ms,
            "ms"
        )

    if duration_ms is not None:
        print(
            "Duration:",
            duration_ms,
            "ms"
        )

    print("--------------------------------")


if __name__ == "__main__":
    main()