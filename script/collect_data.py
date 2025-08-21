from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get

load_dotenv()

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

def get_token():
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def get_tracks_from_playlist(token, playlistID):
    url = f"https://api.spotify.com/v1/playlists/{playlistID}/tracks"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

token = get_token()
trackInformation = get_tracks_from_playlist(token, "5EXeiN2jugC9vnxx2WpxuP")
print(trackInformation)