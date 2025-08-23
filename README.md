# Spotify Playlist Comparator

A command-line tool to analyze and compare two Spotify playlists, providing a detailed similarity score based on various musical metrics.

## Features

* Detailed comparison of tracks, artists, popularity, and release year distributions.
* Calculates an overall weighted compatibility score.
* User-configurable weights to customize the scoring algorithm.
* Clean, colorized, and easy-to-read output in the terminal with the `rich` and `click` libraries.

## Important Note

Due to Spotify API limitations, private playlists and playlists created *by* Spotify are unable to be used with this tool.

Additionally, this is intended as an educational project and will most likely not be supported after release. Feel free to fork this project and expand on it yourself!

## Setup

1.  **Set up a Virtual Environment** It is highly recommended to use a Python virtual environment to manage dependencies, though not required.

2.  **Install Dependencies** After activating your virtual environment, install all required dependencies from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Provide API Credentials** Create a file named `.env` in the root directory of the project. Place your own Spotify Client ID and Client Secret in this file, formatted exactly as shown below.
    ```
    SPOTIFY_CLIENT_ID="YOUR_CLIENT_ID_HERE"
    SPOTIFY_CLIENT_SECRET="YOUR_CLIENT_SECRET_HERE"
    ```

## Usage

### Basic Comparison
To run a comparison with default weights, provide two playlist URLs.

```bash
python app/main.py <PLAYLIST_URL_1> <PLAYLIST_URL_2>
```

## Using Custom Weights

You can add custom weight options by using the -w or --weight flag. Note that the format is Category=Value.

The available categories are "Tracks", "Artists", "Popularity", and "Release Year".

Example:
```bash
python app/main.py <URL1> <URL2> -w "Artists=0.6" -w "Popularity=0.2"
```

## Help

To see all available commands and options, use the --help flag.
```bash
python app/main.py --help
```