# Testanleitung für das RAG-Artefakt (Masterarbeit)

Diese Anleitung erklärt Schritt-für-Schritt, wie Sie das RAG (Retrieval-Augmented Generation) System lokal testen können.

## 📋 Voraussetzungen

### 1. Systemvoraussetzungen

- **Python 3.8 oder höher** (empfohlen: Python 3.11)
- **Git** (optional, für Repository-Klon)
- **Internetverbindung** (für OpenAI API Calls)
- **Mindestens 2GB freier RAM**

### 2. OpenAI API Key

Sie benötigen einen eigenen OpenAI API Key:

1. Gehen Sie zu https://platform.openai.com/api-keys
2. Erstellen Sie einen neuen API Key (oder verwenden Sie einen bestehenden)
3. Notieren Sie den Key für Schritt 4

## 🚀 Installation & Setup

### Schritt 1: Repository klonen

```bash
# Repository klonen
git clone [REPOSITORY_URL]
cd MA_MVP_Prototype_TEST
```

### Schritt 2: Virtuelle Umgebung erstellen

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Schritt 3: Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### Schritt 4: Umgebungsvariablen setzen

Erstellen Sie eine `.env` Datei im Projektverzeichnis:

```bash
# .env Datei erstellen
cat > .env << EOF
OPENAI_API_KEY=IHR_API_KEY_HIER
CHROMA_PERSIST_DIR=./chroma_db
EOF
```

**Wichtig:** Ersetzen Sie `IHR_API_KEY_HIER` mit Ihrem echten OpenAI API Key.

## 🏃‍♀️ System starten

### Schritt 5: Server starten

```bash
fastapi dev backend/app.py
```

Sie sollten folgende Ausgabe sehen:

```
INFO:     Willkommen to FastAPI on Vercel 🚀
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Schritt 6: Browser öffnen

Öffnen Sie Ihren Browser und gehen Sie zu:

```
http://localhost:8000
```

## 🧪 Testen des Systems

### Test 1: Oberfläche erkunden

Die Web-Oberfläche hat zwei Hauptbereiche:

1. **Linke Seite**: Chat-Historie (anfangs leer)
2. **Rechte Seite**: Datei-Upload-Bereich

### Test 2: Beispiel-Dateien hochladen

Im Projektordner `data/` finden Sie Testdateien:

- `JAB_Bitpanda_2022.pdf` / `.json`
- `JAB_Maresi_2022.pdf` / `.json`
- `JAB_Senna_2022.pdf` / `.json`
- `JAB_Smarter_Ecommerce_GmbH_2022.pdf` / `.json`

**So laden Sie Dateien hoch:**

1. Ziehen Sie eine PDF- oder JSON-Datei in den rechten Bereich
2. ODER klicken Sie "Datei auswählen" und wählen Sie eine Datei
3. Das System verarbeitet die Datei automatisch (ca. 10-30 Sekunden)

### Test 3: Fragen stellen

Stellen Sie Fragen zu den hochgeladenen Daten:

**Einfache Faktenfragen:**

```
Was war der Umsatz von Bitpanda GmbH in 2022?
Was waren die Gesamtaktiva von Maresi GmbH in 2022?
Was war der Jahresüberschuss von Senna GmbH in 2022?
```

**Vergleichende Fragen:**

```
Welche Firma hatte den höchsten Umsatz 2022?
Welche Firma hatte die niedrigsten Gesamtaktiva?
```

### Test 4: Antworten analysieren

Das System zeigt für jede Antwort:

- **Antexttext** (generiert durch KI)
- **Quellenangaben** (welche Datei verwendet wurde)
- **Konfidenz-Score** (wie sicher ist die Antwort, 0-100%)
- **Semantisches Mapping** (im Hintergrund: Deutsch → Englisch)

## 🔧 Fehlerbehebung

### Häufige Probleme:

#### 1. "ModuleNotFoundError"

```bash
# Falls Module fehlen:
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### 2. OpenAI API Key Fehler

- Prüfen Sie, ob der API Key in `.env` korrekt ist
- Prüfen Sie, ob Guthaben auf dem OpenAI Account vorhanden ist
- Testen Sie den Key: `curl https://api.openai.com/v1/models -H "Authorization: Bearer IHR_KEY"`

#### 3. Server startet nicht

```bash
# Alternative Startmethode:
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Dateien werden nicht verarbeitet

- Prüfen Sie, ob die Dateien im `data/` Ordner sind
- Prüfen Sie Konsolenausgabe auf Fehlermeldungen
- Versuchen Sie eine kleinere Datei zuerst

## 📊 Erweiterte Tests (optional)

### Evaluation-Skripte ausführen

```bash
# Semantic Mapping Evaluation
python backend/evaluate.py

# RAGAS Faithfulness Evaluation
python backend/evaluate_ragas.py
```

### Datenbank zurücksetzen

```bash
# ChromaDB löschen (bei Problemen)
rm -rf chroma_db/
```

## 🎯 Erwartetes Verhalten

### Bei erfolgreichem Test sollten Sie sehen:

1. **Datei-Upload**: Fortschrittsanzeige, dann "Upload erfolgreich"
2. **Fragen beantworten**: Antwort innerhalb 5-10 Sekunden
3. **Quellenangaben**: Korrekte Dateinamen und Jahre
4. **Konfidenz-Score**: Meist über 80% für einfache Fakten

### Beispiel-Interaktion:

```
Sie: Was war der Umsatz von Bitpanda GmbH in 2022?
System: Der Umsatz von Bitpanda GmbH betrug 2022 € 123.456.789,00.
Quellen: JAB_Bitpanda_2022.pdf (2022)
Konfidenz: 92%
```

## 📞 Support

Bei Problemen kontaktieren Sie bitte:

- **Patrick Roith** (Masterarbeit-Autor)
- **E-Mail**: [IHRE_EMAIL]
- **Telefon**: [IHRE_TELEFONNUMMER]

## 📝 Notizen für die Betreuerin

### Was das System demonstriert:

1. **Automatische Dokumentenverarbeitung**: PDF & JSON Ingestion
2. **Semantisches Mapping**: Deutsche Finanzbegriffe → Englische Standardfelder
3. **RAG-Architektur**: Retrieval + Generation mit Quellennachweis
4. **Konfidenz-Bewertung**: Transparente Unsicherheitsangabe

### Evaluation-Kriterien (aus der Arbeit):

- **Präzision Semantic Mapping**: ≥85% (50-Begriffe Gold Standard)
- **Faithfulness Score**: ≥85% (30 Testfragen)
- **Zeit-Reduktion**: ≥75% vs. manuelle Verarbeitung

### Testdauer empfohlen: 15-30 Minuten

---

**Viel Erfolg beim Testen!** 🚀

_Letzte Aktualisierung: $(date)_
