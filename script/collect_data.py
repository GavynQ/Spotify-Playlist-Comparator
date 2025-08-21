from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get, exceptions
import time

# Load environment variables for credentials
load_dotenv() 
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

def get_token():
    
    # Obtains an access token from the Spotify API using the Client Credentials Flow
    # Returns a string with a Spotify API access token

    # Exit program if credentials not loaded properly
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("Spotify client ID or secret not found in environment variables.")
    
    # Combine client id and client secret and encode into base64 for API use 
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token" # Endpoint for access tokens
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    try:
        # Makes post request and parses the JSON response
        result = post(url, headers=headers, data=data)
        result.raise_for_status() # Exit program if HTTP request not successful
        json_result = json.loads(result.content)
        token = json_result["access_token"]
        return token
    except exceptions.RequestException as e:
        print(f"Error requesting Spotify token: {e}")
        raise # Prevent script from continuing to run
    except KeyError:
        print("Error: 'access_token' not found in the response from Spotify")
        raise # Prevent script from continuing to run

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

    playlist1_trackIDList = []
    playlist2_trackIDList = []

    playlist1_popularityList = []
    playlist2_popularityList = []

    playlist1_releaseYearList = []
    playlist2_releaseYearList = []

    playlist1_artistIDList = []
    playlist2_artistIDList = []

    for item in playlist1Data:
        playlist1_trackIDList.append(item['track_id'])
        playlist1_popularityList.append(item['popularity'])
        playlist1_releaseYearList.append(item['release_year'])
        for artist in item['artist_ids']: # Some tracks have multiple artists that need to be split up
            playlist1_artistIDList.append(artist)

    for item in playlist2Data:
        playlist2_trackIDList.append(item['track_id'])
        playlist2_popularityList.append(item['popularity'])
        playlist2_releaseYearList.append(item['release_year'])
        for artist in item['artist_ids']: # Some tracks have multiple artists that need to be split up
            playlist2_artistIDList.append(artist)

    # Popularity similarity calculated using normalized difference of average popularities
    avg_pop1 = sum(playlist1_popularityList) / len(playlist1_popularityList)
    avg_pop2 = sum(playlist2_popularityList) / len(playlist2_popularityList)
    pop_diff = abs(avg_pop1 - avg_pop2)

    # Year similarity calculated using average difference between playlists in comparision to total year range between playlists (Ex: 2005 vs 2006 has a higher similarity score the greater the difference between the oldest song and newest song)
    min_year = min(min(playlist1_releaseYearList), min(playlist2_releaseYearList))
    max_year = max(max(playlist1_releaseYearList), max(playlist2_releaseYearList))
    year_range = max_year - min_year
    if year_range == 0:
        yearSimilarity = 1.0
    avg_year1 = sum(playlist1_releaseYearList) / len(playlist1_releaseYearList)
    avg_year2 = sum(playlist2_releaseYearList) / len(playlist2_releaseYearList)
    year_diff = abs(avg_year1 - avg_year2)

    trackSimilarity = compare_playlists(playlist1_trackIDList, playlist2_trackIDList)
    artistSimilarity = compare_playlists(playlist1_artistIDList, playlist2_artistIDList)
    popularitySimilarity = (1 - (pop_diff / 100)) * 100
    yearSimilarity = (1 - (year_diff / year_range)) * 100

    scores = {
        "Tracks" : trackSimilarity,
        "Artists" : artistSimilarity,
        "Popularity" : popularitySimilarity,
        "Release Year" : yearSimilarity
    }

    return scores

token = get_token()
playlist1Data = get_playlist_data(token, "37c9gzsiHgEo8xcYeRhOcw") # hamilton
playlist2Data = get_playlist_data(token, "2dfRb8iX2N30YUwXZjHjnA") # my playlist
print(get_similarity_scores(playlist1Data, playlist2Data))


