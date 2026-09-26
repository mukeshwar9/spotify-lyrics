import re
import requests

LRCLIB_URL = "https://lrclib.net/api/get"


def fetch_lyrics(track_name: str, artist_name: str, album_name: str = "") -> dict:
    params = {"track_name": track_name, "artist_name": artist_name}
    if album_name:
        params["album_name"] = album_name
    try:
        resp = requests.get(LRCLIB_URL, params=params, timeout=15)
        if resp.status_code != 200:
            return {"synced": None, "plain": None}
        data = resp.json()
        synced_raw = data.get("syncedLyrics")
        plain = data.get("plainLyrics")
        synced = _parse_lrc(synced_raw) if synced_raw else None
        return {"synced": synced, "plain": plain}
    except Exception:
        return {"synced": None, "plain": None}


def _parse_lrc(lrc_text: str) -> list:
    pattern = re.compile(r'\[(\d+):(\d+(?:\.\d+)?)\](.*)')
    lines = []
    for line in lrc_text.splitlines():
        m = pattern.match(line.strip())
        if m:
            minutes = int(m.group(1))
            seconds = float(m.group(2))
            text = m.group(3).strip()
            lines.append((minutes * 60 + seconds, text))
    return sorted(lines, key=lambda x: x[0])


def current_line_index(synced: list, position: float) -> int:
    idx = 0
    for i, (ts, _) in enumerate(synced):
        if ts <= position:
            idx = i
        else:
            break
    return idx
