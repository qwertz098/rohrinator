# Rohrinator - ANSI Vorschweißflansch 3D Viewer

Generiert einen ANSI B16.5 Vorschweißflansch (Weld Neck Flange) mit Python CadQuery und zeigt ihn interaktiv in einem Three.js Webviewer an.

## Installation

```bash
# Virtuelle Umgebung erstellen (empfohlen)
python -m venv venv
venv\Scripts\activate  # Windows
# oder: source venv/bin/activate  # Linux/Mac

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## Verwendung

### 1. STL-Modell generieren

```bash
python weld_neck_flange.py
```

Dies erstellt:
- `weld_neck_flange.stl` - für den Web-Viewer
- `weld_neck_flange.step` - für CAD-Import

### 2. Viewer starten

Öffnen Sie `viewer.html` in einem Webbrowser. 

**Wichtig:** Aufgrund von CORS-Einschränkungen muss die HTML-Datei über einen lokalen Server ausgeliefert werden:

```bash
# Mit Python
python -m http.server 8000

# Dann im Browser öffnen:
# http://localhost:8000/viewer.html
```

## Flansch-Spezifikationen

| Parameter | Wert |
|-----------|------|
| Nennweite | NPS 2" (DN50) |
| Druckklasse | Class 150 |
| Norm | ANSI B16.5 |
| Flansch-Außen-Ø | 152.4 mm |
| Lochkreis-Ø | 120.6 mm |
| Bolzenlöcher | 4× Ø19 mm |
| Flanschdicke | 22.2 mm |
| Halslänge | 66.5 mm |

## Viewer-Funktionen

- **Maus-Steuerung:** Linke Taste = Drehen, Mausrad = Zoom, Rechte Taste = Verschieben
- **Materialansichten:** Stahl-Optik, Drahtgitter, Röntgen
- **Ansichten:** Vorne, Oben, Seite, Isometrisch
- **Auto-Rotation:** Ein/Ausschaltbar

## Projektstruktur

```
rohrinator/
├── weld_neck_flange.py    # CadQuery Flansch-Generator
├── viewer.html            # Three.js 3D-Viewer
├── weld_neck_flange.stl   # Generierte STL-Datei
├── weld_neck_flange.step  # Generierte STEP-Datei
├── requirements.txt       # Python-Abhängigkeiten
└── README.md
```

## Anpassung

Die Flansch-Dimensionen können im Python-Skript angepasst werden. Die Parameter sind nach ANSI B16.5 Standard benannt und kommentiert.
