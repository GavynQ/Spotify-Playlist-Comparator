from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get
import time

load_dotenv()

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")


def get_token():
    
    # Obtains an access token from the Spotify API using the Client Credentials Flow
    # Returns a string with a Spotify API access token

    # Combine client id and client secret and encode into base64 for API use 
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token" # Spotify Endpoint for token access
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    # Makes post request and parses the JSON response
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    
    # Constructs the authorization header required for Spotify API requests
    # Returns a dictionary containing the formatted header

    return {"Authorization": "Bearer " + token}

def get_tracks_from_playlist(token, playlistID):

    # Fetches all track IDs from a given playlist ID
    # Returns a list of all track IDs from the specified playlist

    url = f"https://api.spotify.com/v1/playlists/{playlistID}/tracks"
    headers = get_auth_header(token)
    
    track_ids = []
    while url:
        result = get(url, headers=headers)
        json_result = json.loads(result.content)
    
        for item in json_result['items']:
            track_ids.append(item['track']['id'])
        
        url = json_result.get('next') # Continues collecting track IDs from playlist if over 100 track limit for one API call

        if url:
            time.sleep(0.1) # Avoids API rate limit
    
    return track_ids

token = get_token()
trackInformation = get_tracks_from_playlist(token, "5EXeiN2jugC9vnxx2WpxuP")
print(trackInformation)
print(len(trackInformation))