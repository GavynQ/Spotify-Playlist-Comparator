import spotify_analyzer
import click

DEFAULT_WEIGHTS = {
    "Tracks": 0.15,
    "Artists": 0.40,
    "Popularity": 0.35,
    "Release Year": 0.10
}

@click.command()
@click.argument("playlist1_url")
@click.argument("playlist2_url")
@click.option(
    "--weight", "-w",
    multiple = True,
    type = str,
    help = "Set a custom weightr for a score category. Format: 'Category=Value'"
            " (ex: -w 'Artists=0.6' sets artist weight to 60%). Can be used multiple times."
            " Available Categories: Tracks, Artists, Popularity, Release Year "
)
def compare_playlists(playlist1_url, playlist2_url, weight):

    # A CLI tool to compare two spotify playlists
    print("--- Starting Comparison ---")
    print(f"Platlist 1: {playlist1_url}")
    print(f"Playlist 2: {playlist2_url}")

    custom_weights = DEFAULT_WEIGHTS.copy()
    # Only sort through custom weights if provided by user
    if weight:
        print("\nApplying custom weights provided by user...")
        for item in weight:
            try:
                category, value = item.split('=')
                if category in custom_weights:
                    custom_weights[category] = float(value)
                else:
                    print(f"Warning: Unknown category '{category}'. Ignoring...")
            except ValueError:
                print(f"Warning: Could not parse '{item}'. Ignoring...")
        
    print("\n--- Final Weights Being Used ---")
    print(f"Tracks: {custom_weights["Tracks"]}")
    print(f"Artists: {custom_weights["Artists"]}")
    print(f"Popularity: {custom_weights["Popularity"]}")
    print(f"Release Year: {custom_weights["Release Year"]}")

    print("\nComparing your playlists...")

    # Extract playlist IDs from urls (spotify.com/playlist/ID)
    playlist1_ID = playlist1_url.split('/')[-1]
    playlist2_ID = playlist2_url.split('/')[-1]

    raw_scores = spotify_analyzer.get_scores(playlist1_ID, playlist2_ID)
    weighted_score = (raw_scores["Tracks"] * custom_weights["Tracks"] + 
                      raw_scores["Artists"] * custom_weights["Artists"] + 
                      raw_scores["Popularity"] * custom_weights["Popularity"] + 
                    raw_scores["Release Year"] * custom_weights["Release Year"])
        
    print(f"\nThe overall compatibility score is {weighted_score}%")

if __name__ == "__main__":
    compare_playlists()