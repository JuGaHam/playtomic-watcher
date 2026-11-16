#!/usr/bin/env python3
"""
Playtomic-Event-Wächter
Prüft öffentliche Playtomic-Event-Seiten und schickt eine Push-Nachricht über ntfy,
sobald sich jemand abmeldet bzw. ein Platz frei wird.

Konfiguration:
  - events.txt: eine Event-URL pro Zeile (Zeilen mit # werden ignoriert)
  - Umgebungsvariable NTFY_TOPIC: dein geheimer ntfy-Kanalname
  - optional NTFY_SERVER (Standard: https://ntfy.sh)
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

BASE = Path(__file__).parent
EVENTS_FILE = BASE / "events.txt"
STATE_FILE = BASE / "state.json"
NTFY_SERVER = os.environ.get("NTFY_SERVER", "https://ntfy.sh").rstrip("/")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (playtomic-watcher; private use)",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def parse(html: str):
    """Liest 'angemeldet/maximal' und den Titel aus der Seite."""
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    # Überschrift der Spielerliste, z. B. "Spieler (11/12)", "Players (11/12)", "Giocatori (12/12)"
    m = re.search(r"\(\s*(\d{1,3})\s*/\s*(\d{1,3})\s*\)", text)
    if not m:
        # Fallback: "12/12 Plätze", "11/12 spots", "12/12 posti"
        m = re.search(r"(\d{1,3})\s*/\s*(\d{1,3})\s*(?:Plätze|Platz|spots|places|posti|plazas)", text, re.I)
    if not m:
        return None

    title_m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    title = title_m.group(1).strip() if title_m else "Playtomic-Event"
    title = re.sub(r"\s*[|–-]\s*Playtomic.*$", "", title)
    return {"registered": int(m.group(1)), "max": int(m.group(2)), "title": title}


def notify(title: str, message: str, url: str):
    if not NTFY_TOPIC:
        print(f"[kein NTFY_TOPIC gesetzt] {title}: {message}")
        return
    payload = {
        "topic": NTFY_TOPIC,
        "title": title,
        "message": message,
        "priority": 4,
        "tags": ["tennis"],
        "click": url,
    }
    req = urllib.request.Request(
        NTFY_SERVER,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(req, timeout=15)


def main():
    urls = [
        line.strip()
        for line in EVENTS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
    errors = 0
    log = []

    for url in urls:
        try:
            html = fetch(url)
        except Exception as e:  # Netzwerkfehler etc.
            print(f"Fehler bei {url}: {e}", file=sys.stderr)
            log.append(f"FEHLER {url}: {e}")
            errors += 1
            continue
        info = parse(html)
        if info is None:
            print(f"Konnte Teilnehmerzahl nicht finden: {url}", file=sys.stderr)
            snippet = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))[:300]
            log.append(f"NICHT GEFUNDEN {url} ({len(html)} Zeichen): {snippet}")
            errors += 1
            continue

        reg, mx, title = info["registered"], info["max"], info["title"]
        free = mx - reg
        prev = state.get(url)
        print(f"{title}: {reg}/{mx} ({free} frei)")
        log.append(f"OK {title}: {reg}/{mx} ({free} frei)")

        if prev is not None and reg < prev["registered"]:
            weg = prev["registered"] - reg
            notify(
                f"Abmeldung: {title}",
                f"{weg} Spieler weniger – jetzt {reg}/{mx}, {free} Platz/Plätze frei. Tippen zum Öffnen.",
                url,
            )

        state[url] = {"registered": reg, "max": mx}

    # entfernte Events aus dem Zustand löschen
    state = {u: s for u, s in state.items() if u in urls}
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))

    (BASE / "status.txt").write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
