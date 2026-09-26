from rich.console import Console
from rich.text import Text
from rich.table import Table

console = Console()


def build_panel(track, synced, plain, idx):
    lyric = synced[idx][1] if synced and idx < len(synced) else ("♪" if synced else "No lyrics")
    if not lyric:
        lyric = "♪"
    track_info = f"{track['name']} · {track['artist']}"

    row = Table.grid(expand=True)
    row.add_column(justify="left", ratio=1)
    row.add_column(justify="right")
    row.add_row(
        Text(lyric, style="bold bright_white"),
        Text(track_info, style="dim"),
    )
    return row


def idle_panel(message: str):
    row = Table.grid(expand=True)
    row.add_column(justify="left", ratio=1)
    row.add_column(justify="right")
    row.add_row(Text(message, style="dim italic"), Text(""))
    return row


def format_status(track, synced, plain, idx):
    if not track:
        return ""
    lyric = synced[idx][1] if synced and idx < len(synced) else ""
    return lyric.strip()
