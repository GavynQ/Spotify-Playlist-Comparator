from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get
import time

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


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

def get_playlist_data(token, playlistID):

    # Fetches detailed data for all tracks in a given playlist
    # Returns a list of dictionaries, where each dictionary represents a track and contains its ID, popularity, release year, and artist IDs

    fields_query = "items(track(id,popularity,album(release_date),artists(id))),next"
    url = f"https://api.spotify.com/v1/playlists/{playlistID}/tracks"
    headers = get_auth_header(token)
    
    playlist_items = []
    while url:
        try:
            result = get(url, headers=headers, params={"limit": 100, "fields": fields_query})
            result.raise_for_status()
            json_result = result.json()
        
            # Processes each item from the current page of results
            for item in json_result.get('items', []):
                track = item.get('track')
                if not track or not track.get('id'):
                    continue # Skip if the track is null or has no ID
                
                # Extracts the year from the release_date string (e.g., '2024-08-21' -> 2024)
                release_year = 0
                if track.get('album') and track['album'].get('release_date'):
                    release_year = int(track['album']['release_date'].split('-')[0])

                # Extracts a list of artist IDs from the list of artist objects
                artist_ids = [artist['id'] for artist in track.get('artists', []) if artist.get('id')]

                playlist_items.append({
                    "track_id": track['id'],
                    "popularity": track.get('popularity', 0),
                    "release_year": release_year,
                    "artist_ids": artist_ids
                })
            
            # Get the URL for the next page
            url = json_result.get('next')
            if url:
                time.sleep(0.1) # Avoid API rate limit
                
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    
    return playlist_items

def compare_playlists(playlist1Data, playlist2Data):
    
    # Compares set of data (track, artist, etc) from two playlists and generate similarity scores for each
    # Returns a float representing the similarity percentage

    set1 = set(playlist1Data)
    set2 = set(playlist2Data)

    intersection = set1.intersection(set2)
    union = set1.union(set2)

    if not union:
        return 0.0
    
    similarity = len(intersection) / len(union) # Calculate the Jaccard similarity score

    return similarity * 100 # Return similarity as percentage

def get_similarity_scores(playlist1Data, playlist2Data):

    # Sort through specific data types in both playlist tracks and get similarity scores for each using a Jaccard index



    for item in playlist1Data:
        
    
    track_similarity = compare_playlists(playlist1Data[])

