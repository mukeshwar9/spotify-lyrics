import subprocess


def _run(script: str) -> str:
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def get_current_track():
    # single AppleScript call returns all fields at once — avoids 4 round-trips
    script = """
    tell application "System Events"
        if not (exists process "Spotify") then return "NOT_RUNNING"
    end tell
    tell application "Spotify"
        set s to player state as string
        if s is not "playing" and s is not "paused" then return "STOPPED"
        return s & "|" & (name of current track) & "|" & (artist of current track) & "|" & (album of current track)
    end tell
    """
    out = _run(script)
    if out in ("NOT_RUNNING", "STOPPED", ""):
        return None
    parts = out.split("|", 3)
    if len(parts) < 4:
        return None
    return {"state": parts[0], "name": parts[1], "artist": parts[2], "album": parts[3]}


def get_player_position() -> float:
    try:
        return float(_run('tell application "Spotify" to player position'))
    except ValueError:
        return 0.0
