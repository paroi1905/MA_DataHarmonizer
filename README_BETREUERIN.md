# RAG Financial Assistant - Masterarbeit Artefakt

## 🎯 Kurzübersicht für Betreuerin

Dieses System ist ein **Retrieval-Augmented Generation (RAG) Framework** für die automatische Verarbeitung von österreichischen Jahresabschlüssen (PDF/JSON).

### Kernfunktionen:

1. **Dual-Path Ingestion**: Verarbeitet PDFs (OCR) und JSONs (strukturiert)
2. **Semantisches Mapping**: Deutsche Finanzbegriffe → Englische Standardfelder
3. **RAG mit Quellennachweis**: Antworten mit exakten Quellenangaben
4. **Konfidenz-Scoring**: Transparente Unsicherheitsangabe

## ⚡ Schnellstart (5 Minuten)

```bash
# 1. Repository klonen
git clone [URL]
cd MA_MVP_Prototype_TEST

# 2. Virtuelle Umgebung
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Abhängigkeiten
pip install -r requirements.txt

# 4. .env Datei erstellen (mit Ihrem OpenAI Key)
echo "OPENAI_API_KEY=IHR_KEY_HIER" > .env

# 5. Server starten
fastapi dev backend/app.py

# 6. Browser öffnen: http://localhost:8000
```

## 🧪 Erste Tests

1. **Datei hochladen**: Ziehen Sie `data/JAB_Bitpanda_2022.pdf` in die Oberfläche
2. **Frage stellen**: "Was war der Umsatz von Bitpanda GmbH in 2022?"
3. **Antwort analysieren**: Quellen + Konfidenz prüfen

## 📁 Projektstruktur

```
backend/           # Python FastAPI Backend
├── app.py         # REST API Endpoints
├── udm.py         # Unified Document Model (Schema)
├── semantic.py    # Semantisches Mapping
├── ingest.py      # Dokumentenverarbeitung
├── rag.py         # RAG Pipeline
└── evaluate.py    # Evaluation Skripte

static/            # Frontend (HTML/CSS/TypeScript)
data/              # Testdaten & Evaluation-Datasets
```

## 🔍 Was zu testen ist

### A. Funktionale Tests:

- [ ] PDF Upload & Verarbeitung
- [ ] JSON Upload & Verarbeitung
- [ ] Semantisches Mapping (Deutsch → Englisch)
- [ ] Quellennachweis in Antworten
- [ ] Konfidenz-Scoring

### B. Beispiel-Fragen:

```
1. "Umsatz Bitpanda 2022?"
2. "Gesamtaktiva Maresi 2022?"
3. "Jahresüberschuss Senna 2022?"
4. "Welche Firma höchster Umsatz?"
```

### C. Evaluation (optional):

```bash
# Semantic Mapping Evaluation
python backend/evaluate.py

# RAGAS Faithfulness Evaluation
python backend/evaluate_ragas.py
```

## ⚠️ Bekannte Einschränkungen

1. **OpenAI API benötigt**: Kosten ca. $0.01 pro Test
2. **Lokale Verarbeitung**: Keine Cloud-Dienste außer OpenAI
3. **Deutsche Finanzdokumente**: Optimiert für österreichische UGB-Berichte
4. **PDF Qualität**: Benötigt maschinenlesbaren Text

## 📞 Bei Problemen

1. **Server startet nicht**: `uvicorn backend.app:app --reload`
2. **Module fehlen**: `pip install -r requirements.txt --force-reinstall`
3. **API Key Fehler**: Prüfen Sie `.env` Datei und OpenAI Guthaben
4. **Kontakt**: Patrick Roith - [KONTAKTINFO]

## 🎓 Akademischer Kontext

Dieses Artefakt implementiert die **vier Iterationen** aus dem Thesis-Design:

1. **Grundarchitektur**: UDM + Basis-Ingestion
2. **Semantisches Mapping**: Hybrid (Dictionary + LLM)
3. **RAG Optimierung**: Retrieval + Generation
4. **Evaluation Framework**: Drei evaluierte Methoden

**Evaluation Thresholds:**

- Semantic Mapping Precision: ≥85%
- Faithfulness Score: ≥85%
- Time Reduction: ≥75% vs. manuell

---

**Testdauer empfohlen: 15-30 Minuten**

_Viel Erfolg bei der Evaluation!_
