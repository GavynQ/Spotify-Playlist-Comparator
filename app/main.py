import spotify_analyzer
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.status import Status

console = Console()

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
    help = "Set a custom weight for a score category. Format: 'Category=Value'"
            " (ex: -w 'Artists=0.6' sets artist weight to 60%). Can be used multiple times."
            " Available Categories: Tracks, Artists, Popularity, Release Year "
)
def compare_playlists(playlist1_url, playlist2_url, weight):

    # A CLI tool to compare two spotify playlists
    console.print(Panel(
        f"[bold]Playlist 1:[/] {playlist1_url}\n[bold]Playlist 2:[/] {playlist2_url}",
        title="[bold blue]Starting Comparison[/bold blue]",
        border_style="blue",
        expand=False
    ))

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

    weights_table = Table(title="Final Weights Being Used", show_header=True, header_style="bold magenta")
    weights_table.add_column("Category", style="cyan")
    weights_table.add_column("Weight", style="green")
    for category, value in custom_weights.items():
        weights_table.add_row(category, f"{value:.2%}") # Formats as percentage
    console.print(weights_table)

    raw_scores = {}
    # Use a status spinner while waiting for API results
    with Status("[bold green]Comparing playlists...[/bold green]", spinner="dots") as status:
        # Extract playlist IDs from urls (spotify.com/playlist/ID)
        playlist1_ID = playlist1_url.split('/')[-1]
        playlist2_ID = playlist2_url.split('/')[-1]
        raw_scores = spotify_analyzer.get_scores(playlist1_ID, playlist2_ID)

    weighted_score = sum(raw_scores[category] * custom_weights[category] for category in raw_scores)
        
    results_table = Table(title="Comparison Results", show_header=False)
    results_table.add_column("Metric", style="cyan")
    results_table.add_column("Score", style="yellow")
    for category, score in raw_scores.items():
        results_table.add_row(category, f"{score:.2f}%")
    
    # Add a final row for the overall score
    results_table.add_section()
    results_table.add_row("[bold]Overall Compatibility[/bold]", f"[bold green]{weighted_score:.2f}%[/bold green]")
    
    console.print(results_table)

if __name__ == "__main__":
    compare_playlists()