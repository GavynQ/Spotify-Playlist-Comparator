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
        result = get(url, headers=headers, params={"limit": 100, "fields": "items(track(id)),next"})
        json_result = json.loads(result.content)
    
        for item in json_result['items']:
            track_ids.append(item['track']['id'])
        
        url = json_result.get('next') # Continues collecting track IDs from playlist if over 100 track limit for one API call

        if url:
            time.sleep(0.1) # Avoids API rate limit
    
    return track_ids

def get_playlist_information(playlistID):
    
    # Condensed function to get track IDs from playlist in one function call
    # Returns list of track IDs from playlist
    
    token = get_token()
    return get_tracks_from_playlist(token, playlistID)

def compare_playlists(trackIDList1, trackIDList2):
    
    # Compares the tracks from two playlists and returns a similarity score using a Jaccard index
    # Returns a float representing the similarity percentage

    set1 = set(trackIDList1)
    set2 = set(trackIDList2)

    intersection = set1.intersection(set2)
    union = set1.union(set2)

    if not union:
        return 0.0
    
    similarity = len(intersection) / len(union) # Calculate the Jaccard similarity score

    return similarity * 100 # Return similarity as percentage

print(get_playlist_information("5EXeiN2jugC9vnxx2WpxuP"))
