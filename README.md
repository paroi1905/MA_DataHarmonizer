# Financial RAG Assistant Prototype

Master's Thesis — Patrick Roith, BSc.

This is a Retrieval-Augmented Generation (RAG) framework designed to ingest, semantically map, chunk, and query heterogeneous annual financial reports (PDFs and JSONs) from Austrian companies.

## 🏗 Modular Architecture

The framework has been completely refactored to prioritize domain-driven design, maintainability, and clean UI aesthetics.

### 🌐 Frontend (`/static/`)
A minimalist, modern, glassmorphic UI built in Vanilla HTML, CSS, and TypeScript.
- **`index.html`**: Defines the dashboard app wrapper, chat interface, and the side-panel document upload dropzone.
- **`styles.css`**: Premium glassmorphic styling and dark mode design tokens.
- **`app.ts`**: Handles user input, querying the backend `/query` endpoint, displaying sources/confidence scores, and submitting documents targeted explicitly to the `/upload` endpoint.
- *Note:* TypeScript must be compiled via `npx tsc` inside the `/static/` folder (`tsconfig.json` ensures fast skipping of library typings).

### ⚙️ Backend (`/backend/`)
A scalable, modularized Python FastAPI backend driving the RAG intelligence.
1. **`app.py`**: The minimalist API entry point. Mounts the REST routes (`/query`, `/upload`), delegates intelligence to `rag.py`, and statically serves the UI.
2. **`udm.py`**: Defines the `UnifiedDocumentModel` (TypedDict) strictly enforcing consistent schema definitions globally.
3. **`semantic.py`**: The semantic brain. Contains LLM-powered dynamic field mapping (accelerated by our static dictionary), and intelligent semantic chunking.
4. **`ingest.py`**: The orchestrator. Parses raw PDFs and JSONs, passes them to the Semantic models, and pipes the output chunks. Features `ingest_single_file()` to surgically process new UI uploads without costly full-database rebuilds.
5. **`rag.py`**: The Knowledge Engine. Connects to the ChromaDB vector database, manages embeddings, and generates the LangChain conversational retrieval chain with source citations.

## 🚀 Setup & Execution

### 1. Environment Requirements
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_key_here
LANGCHAIN_API_KEY=your_api_key_here   # Optional for LangSmith tracking
CHROMA_PERSIST_DIR=./chroma_db
```

### 2. Run the Server
Activate your virtual environment and start the development server from the **root directory**. This ensures all absolute local imports (`from rag import ...`) resolve perfectly.
```bash
source venv/bin/activate
fastapi dev backend/app.py
```
*Visit `http://127.0.0.1:8000` to interact with the UI.*

### 3. Compile Frontend Changes
If you modify `static/app.ts`, simply jump into the `static` directory and recompile:
```bash
cd static/
npx tsc
cd ..
```

## 🧠 Core Features
- **Intelligent Fast-Path Mapping**: Before triggering expensive LLM calls, the backend checks `data/mapping_dictionary.json` to statically map known financial aliases (e.g. `Gesamtkapital` → `Total Assets`) in under 1 second.
- **Surgical Ingestion**: Uploading files from the frontend dynamically invokes `ingest_single_file()`, processing only the singular new document, vectorizing it, and instantly refreshing the RAG chain's memory context without duplicates.
- **Line-level Citation Accuracy**: The frontend actively displays the exact source document, company fiscal year, and overall RAG pipeline confidence score inline next to the AI's answer.
