# Playtomic-Abmelde-Wächter – Einrichtung

Das Skript ruft alle 5 Minuten deine Playtomic-Events ab. Sinkt die Teilnehmerzahl,
bekommst du sofort eine Push-Nachricht aufs Handy. Tippst du darauf, öffnet sich das Event.

## 1. ntfy aufs Handy (2 Min.)
1. App **ntfy** aus dem Play Store / App Store installieren.
2. „+“ → Thema abonnieren → einen **geheimen, schwer zu ratenden Namen** wählen,
   z. B. `padel-juri-8f3k2q9x`. (Wer den Namen kennt, kann deine Nachrichten lesen.)
3. Xiaomi-Tipp: In den Android-Einstellungen für ntfy **Autostart erlauben** und
   **Akku-Sparmodus: Keine Einschränkungen** setzen, sonst kommen Pushs verspätet.

## 2. GitHub-Repository anlegen (5 Min.)
1. Kostenlosen Account auf github.com anlegen (falls nicht vorhanden).
2. Neues Repository erstellen, **öffentlich** (Public). Bei öffentlichen Repos sind
   GitHub Actions unbegrenzt kostenlos; bei privaten reichen die Freiminuten für
   alle 5 Minuten nicht aus.
3. Die Dateien hochladen: `check.py`, `events.txt` und der Ordner
   `.github/workflows/check.yml` (beim Upload über „Add file → Create new file“
   den Pfad `.github/workflows/check.yml` eintippen und den Inhalt einfügen).

## 3. Geheimen ntfy-Namen hinterlegen
Repository → **Settings → Secrets and variables → Actions → New repository secret**
- Name: `NTFY_TOPIC`
- Wert: dein Themenname aus Schritt 1 (z. B. `padel-juri-8f3k2q9x`)

So steht der Name nicht öffentlich im Repo.

## 4. Events eintragen
`events.txt` bearbeiten und pro Zeile eine Event-URL eintragen
(in der Playtomic-App beim Event auf „Teilen“ → Link kopieren).

## 5. Testen
Repository → **Actions → „Playtomic prüfen“ → Run workflow**.
Im Log sollte z. B. `Americano League: 12/12 (0 frei)` stehen.
Der erste Lauf merkt sich nur den Stand; Pushs kommen ab dem nächsten Lauf bei einer Abmeldung.

Push-Test ohne Abmeldung: im Browser
`https://ntfy.sh/DEIN-THEMA/publish?message=Test` öffnen – die Nachricht sollte am Handy ankommen.

## Gut zu wissen
- GitHub startet zeitgesteuerte Läufe oft mit einigen Minuten Verspätung.
  Realistisch: Meldung 5–15 Minuten nach der Abmeldung.
- Nach 60 Tagen ohne Aktivität im Repo pausiert GitHub zeitgesteuerte Workflows –
  das Skript committet aber bei jeder Änderung den Zustand, das zählt als Aktivität.
  Falls es doch pausiert: unter Actions wieder aktivieren.
- Das ist eine inoffizielle Lösung. Ändert Playtomic die Seite, meldet das Log
  „Konnte Teilnehmerzahl nicht finden“ – dann muss die Erkennung angepasst werden.
- Erledigte Events einfach aus `events.txt` löschen.
