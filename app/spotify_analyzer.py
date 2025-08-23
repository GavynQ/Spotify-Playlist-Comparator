from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get, exceptions
import time
import statistics

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
        json_result = result.json()
        token = json_result["access_token"]
        return token
    except exceptions.RequestException as e:
        print(f"Error requesting Spotify token: {e}")
        raise # Prevent script from continuing to run
    except KeyError:
        print("Error: 'access_token' not found in the response from Spotify")
        raise

def get_auth_header(token):
    
    # Constructs the authorization header required for Spotify API requests using the API token
    # Returns a dictionary containing the formatted header

    return {"Authorization": "Bearer " + token}

def get_playlist_data(token, playlistID):

    # Fetches detailed data for all tracks in a given Spotify playlist
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
        
            # Processes each item from the current batch of results
            for item in json_result.get('items', []):
                track = item.get('track')
                if not track or not track.get('id'):
                    continue # Skip if the track is null or has no ID
                
                # Extracts the year from the release_date string (ex: '2024-08-21' -> 2024)
                release_year = 0
                if track.get('album') and track['album'].get('release_date'):
                    release_year = int(track['album']['release_date'].split('-')[0])

                # Extracts a list of artist IDs from the list of artist objects
                artist_ids = [
                    artist['id'] for artist in track.get('artists', []) 
                    if artist.get('id')
                    ]

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
                
        except exceptions.RequestException as e:
            print(f"An error occured while fetching playlist data: {e}")
            break
        except KeyError as e:
            print(f"Unexpected data structure in API response: missing key {e}")
            break
    
    return playlist_items

def calculate_jaccard_similarity(playlist1Data, playlist2Data):
    
    # Calculates the Jaccard similarity between two sets of data
    # The jaccard similarity is the size of the intersection divided by the size of the union of the two data sets
    # Returns the jaccard similarity score as a percentage between 0.0 and 100.0

    set1 = set(playlist1Data)
    set2 = set(playlist2Data)

    intersection = set1.intersection(set2)
    union = set1.union(set2)

    if not union:
        return 0.0
    
    similarity = len(intersection) / len(union) # Calculate the Jaccard similarity score

    return similarity * 100 # Return similarity as percentage

def get_similarity_scores(playlist1_data, playlist2_data):

    # Calculates similarity scores for tracks, artists, popularity, and release year
    # Returns a dictionary with the similarity scores for each metric

    # No similarity if there is a missing or invalid playlist
    if not playlist1_data or not playlist2_data:
        return {
            "Tracks": 0.0,
            "Artists": 0.0,
            "Popularity": 0.0,
            "Release Year": 0.0,
        }

    p1_track_ids = {item['track_id'] for item in playlist1_data}
    p2_track_ids = {item['track_id'] for item in playlist2_data}

    # Nested for loop to break up tracks that have multiple artists
    p1_artist_ids = {artist for item in playlist1_data for artist in item['artist_ids']}
    p2_artist_ids = {artist for item in playlist2_data for artist in item['artist_ids']}

    p1_popularities = [item['popularity'] for item in playlist1_data]
    p2_popularities = [item['popularity'] for item in playlist2_data]

    # Checks valid release date by checking if year > 0
    p1_release_years = [item['release_year'] for item in playlist1_data if item['release_year'] > 0]
    p2_release_years = [item['release_year'] for item in playlist2_data if item['release_year'] > 0]

    # Jaccard similarity calculations
    track_similarity = calculate_jaccard_similarity(p1_track_ids, p2_track_ids)
    artist_similarity = calculate_jaccard_similarity(p1_artist_ids, p2_artist_ids)

    # Popularity similarity
    avg_pop1 = sum(p1_popularities) / len(p1_popularities) if p1_popularities else 0
    avg_pop2 = sum(p2_popularities) / len(p2_popularities) if p2_popularities else 0
    pop_diff = abs(avg_pop1 - avg_pop2)
    popularity_similarity = max(0.0, (1 - (pop_diff / 100)) * 100)

    # Release year similarity using distribution comparisons
    year_similarity = 0.0
    if p1_release_years and p2_release_years:
        p1_avg_year = sum(p1_release_years) / len(p1_release_years)
        p2_avg_year = sum(p2_release_years) / len(p2_release_years)
        
        p1_std_dev = statistics.stdev(p1_release_years)
        p2_std_dev = statistics.stdev(p2_release_years)
        
        year_avg_diff = abs(p1_avg_year - p2_avg_year)
        std_dev_diff = abs(p1_std_dev - p2_std_dev)

        normalization_factor_avg = 20
        avg_year_similarity = max(0, (1 - (year_avg_diff / normalization_factor_avg))) * 100

        normalization_factor_st_dev = 10
        st_dev_similarity = max(0, (1 - (std_dev_diff / normalization_factor_st_dev))) * 100

        # Accounts for closeness of avg years and the general release range of both playlists
        year_similarity = (avg_year_similarity + st_dev_similarity) / 2

    return {
        "Tracks": round(track_similarity, 2),
        "Artists": round(artist_similarity, 2),
        "Popularity": round(popularity_similarity, 2),
        "Release Year": round(year_similarity, 2)
    }


