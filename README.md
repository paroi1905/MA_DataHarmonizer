# Financial RAG Assistant Prototype

This is a Retrieval-Augmented Generation (RAG) framework designed to ingest, semantically map, chunk, and query heterogeneous annual financial reports (PDFs and JSONs) from Austrian companies.


### Prerequisites

- Python 3.11+
- Node.js (for TypeScript compilation)
- An OpenAI API key

### Setup

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd MA_MVP_Prototype_TEST

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 5. Start the server
fastapi dev backend/app.py
```

Open **http://127.0.0.1:8000** in your browser.

## Usage

### Ask Questions

Type financial questions into the chat. The AI answers using only the ingested documents:

- "What is the revenue of Bitpanda in 2022?"
- "What are the total assets of Maresi GmbH?"
- "Net profit of Senna GmbH?"

### Upload & Ingest Documents

1. Switch to the **Documents** tab
2. Click the upload area and select PDF or JSON files
3. Click **Process Documents** — the files are uploaded and ingested into the vector database
4. Once complete, the document list shows what's available for querying

### Add Your Own Reports

Place `.pdf` or `.json` files in the `data/` folder, then use the Documents tab to ingest them. The system automatically extracts financial fields and creates semantic chunks.

## Project Structure

```
├── backend/
│   ├── app.py          # FastAPI server (REST endpoints, static file serving)
│   ├── rag.py          # RAG pipeline (ChromaDB retriever, LLM generation)
│   ├── ingest.py       # Document processing (PDF/JSON parsing, enrichment)
│   ├── semantic.py     # Semantic mapping + chunking
│   ├── udm.py          # Unified Document Model (schema definition)
│   ├── evaluate.py     # Evaluation suite (mapping precision/recall, faithfulness)
│   └── evaluate_ragas.py  # RAGAS-based faithfulness evaluation
├── static/
│   ├── index.html      # Frontend HTML
│   ├── styles.css      # Styling (dark theme)
│   ├── app.ts          # TypeScript logic
│   └── app.js          # Compiled JavaScript (do not edit directly)
├── data/               # Financial reports + evaluation datasets
├── chroma_db/          # Vector database (auto-created, can be deleted to reset)
└── requirements.txt
```

## Development

### Compile TypeScript

After editing `static/app.ts`:

```bash
cd static && npx tsc && cd ..
```

### Add a New Document

1. Copy the file into `data/`
2. Go to the **Documents** tab in the UI
3. Upload and process it — only the new file is ingested

### Reset the Vector Database

```bash
rm -rf chroma_db/
# Then restart the server
```


## Tech Stack

- **Backend**: Python, FastAPI, LangChain, ChromaDB, OpenAI (GPT-4o-mini)
- **Frontend**: Vanilla TypeScript, HTML, CSS (dark theme)
- **Embeddings**: OpenAI `text-embedding-3-small` (rate-limited, batched)

## Notes

- The server must be started from the project root directory so imports resolve correctly
- The `chroma_db/` folder is auto-created on first startup
- Only `.pdf` and `.json` files are accepted for upload
- TypeScript compilation requires the `tsconfig.json` in the `static/` folder
