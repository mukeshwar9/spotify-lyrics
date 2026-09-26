import sys
import time
from rich.live import Live
from .spotify import get_current_track, get_player_position
from .lyrics import fetch_lyrics, current_line_index
from .renderer import console, build_panel, idle_panel, format_status

POLL_INTERVAL = 0.5
DAEMON_FILE = "/tmp/spotify-lyric"
SONG_FILE = "/tmp/spotify-song"


def run_live():
    track_key = None
    lyrics_data = {"synced": None, "plain": None}
    idx = 0

    with Live(console=console, refresh_per_second=2, screen=True) as live:
        while True:
            track = get_current_track()

            if not track:
                live.update(idle_panel("Waiting for Spotify..."))
                time.sleep(POLL_INTERVAL)
                continue

            key = f"{track['name']}::{track['artist']}"
            if key != track_key:
                track_key = key
                live.update(idle_panel(f"Loading lyrics for {track['name']}..."))
                lyrics_data = fetch_lyrics(track["name"], track["artist"], track.get("album", ""))
                idx = 0

            if track["state"] == "playing":
                position = get_player_position()
                if lyrics_data["synced"]:
                    idx = current_line_index(lyrics_data["synced"], position)

            live.update(build_panel(track, lyrics_data["synced"], lyrics_data["plain"], idx))
            time.sleep(POLL_INTERVAL)


def run_daemon():
    track_key = None
    lyrics_data = {"synced": None, "plain": None}
    idx = 0

    def _write(text):
        with open(DAEMON_FILE, "w") as f:
            f.write(text)

    def _write_song(text):
        with open(SONG_FILE, "w") as f:
            f.write(text)

    try:
        while True:
            track = get_current_track()

            if not track:
                _write("")
                _write_song("")
                time.sleep(POLL_INTERVAL)
                continue

            key = f"{track['name']}::{track['artist']}"
            if key != track_key:
                track_key = key
                idx = 0
                lyrics_data = {"synced": None, "plain": None}
                _write("")
                _write_song(f"{track['name']} – {track['artist']}")
                lyrics_data = fetch_lyrics(track["name"], track["artist"], track.get("album", ""))

            if track["state"] == "playing":
                position = get_player_position()
                if lyrics_data["synced"]:
                    idx = current_line_index(lyrics_data["synced"], position)

            _write(format_status(track, lyrics_data["synced"], lyrics_data["plain"], idx))
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        _write("")
        _write_song("")
    except Exception as e:
        with open("/tmp/spotify-lyric-error.txt", "w") as f:
            import traceback
            f.write(traceback.format_exc())


def main():
    if "--daemon" in sys.argv or "-d" in sys.argv:
        run_daemon()
    else:
        try:
            run_live()
        except KeyboardInterrupt:
            console.print("\n[dim]Stopped.[/dim]")


if __name__ == "__main__":
    main()
