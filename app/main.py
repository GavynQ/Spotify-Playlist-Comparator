import app.spotify_analyzer as spotify_analyzer

def main():
    token = spotify_analyzer.get_token()
    playlist1Data = spotify_analyzer.get_playlist_data(token, "37c9gzsiHgEo8xcYeRhOcw") # hamilton
    playlist2Data = spotify_analyzer.get_playlist_data(token, "2dfRb8iX2N30YUwXZjHjnA") # my playlist
    print(spotify_analyzer.get_similarity_scores(playlist1Data, playlist2Data))

if __name__ == "__main__":
    main()