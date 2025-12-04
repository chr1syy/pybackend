# pybackend
Backend with FastAPI and Postgres

# Dev

1. Clone Repo

2. Copy .env.example to your local .env and change settings

2. Create Virtual Environment
```
python -m venv .venv
source .venv/bin/activate
```
3. Install Requirements
```
pip install -r requirements.txt
```

4. Start DB in Folder db with Docker-Compose up
```
docker-compose -f docker-compose.dev.yml up -d
```

5. Init Database
```
alembic upgrade head
```

6. Start Backend locally
```
uvicorn app.main:app --reload
```

7. Running `pytest` automatically Seeds Admin User with Admin Password and runs the Endpoint tests

Scripts to reset DB or seed an Admin User manually:
```
python3 -m scripts.reset_db
python3 -m scripts.seed_admin
```


# Prod

1. Clone Repo

2. Copy .env.example to your local .env and change settings

3. Start Docker Container
```
docker-compose -f docker-compose.prod.yml up --build
```

# ToDo / Roadmap

- Blitzschutz, Trennungsabstände → neue Endpunkte /calculations/lightning, /calculations/separation
- Erweiterung: Berechnungs-Engine modularisieren → jede Berechnung als Service, leicht erweiterbar
- Erweiterung: Validierung gegen Normen (DIN/VDE‑Tabellen im Backend hinterlegt)

- Formulare für Passwort‑Vergessen (E-Mail eingeben → Code erhalten → neues Passwort setzen)
- UI für Zugangscode‑Eingabe bei Registrierung oder Login
- Erweiterung: Feedback‑Modals (z. B. „Code erfolgreich gesendet“)
- Erweiterung: 2FA‑Dialoge (Code per Mail eingeben)

- Eingabeformular mit allen Variablen (Länge, Strom, Spannung, Spannungsfall in %)
- Ergebnisanzeige mit berechnetem Querschnitt + Empfehlung Standardgröße
- Erweiterung: „Speichern“‑Button → Kabeldaten in DB ablegen
- Erweiterung: Liste gespeicherter Berechnungen → Auswahl + Export als PDF

- Neue Views für Blitzschutz und Trennungsabstände
- Einheitliches Layout wie bei Conversion/CableCalculation
- Erweiterung: Tab‑Navigation für alle Berechnungen (Conversion, Kabel, Blitzschutz, …)
- Erweiterung: Diagramme/Visualisierungen (z. B. Trennungsabstände grafisch darstellen)

- API‑Dokumentation (Swagger/OpenAPI) für alle Berechnungsendpunkte
- Hintergrundjobs für E-Mail‑Versand (Queue, Retry)

- Dashboard mit Übersicht: letzte Berechnungen, gespeicherte Projekte, offene Zertifikate
- Export‑Buttons (PDF/CSV) direkt in den Views
- Responsive Design für mobile Nutzung auf Baustellen

- Versionierung und Anzeige von aktuellen Plänen

