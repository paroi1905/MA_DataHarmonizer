# Feature Request: Documents Tab with Upload, Ingestion and Document List

## Context

This is a FastAPI + ChromaDB RAG prototype for a master's thesis. The frontend is built with vanilla HTML, CSS and JavaScript. The backend is Python FastAPI. The project structure is:

```
MA_MVP_Prototype_TEST/
├── backend/
│   ├── app.py          ← FastAPI server — needs new endpoints
│   ├── ingest.py       ← ingestion pipeline — already works
│   ├── rag.py          ← RAG chain
│   ├── semantic.py     ← chunking
│   └── udm.py          ← Unified Document Model
├── static/
│   ├── index.html      ← frontend — needs Documents tab
│   ├── app.js          ← compiled JS — needs Documents tab logic
│   ├── app.ts          ← TypeScript source — needs Documents tab logic
│   └── styles.css      ← styles — needs Documents tab styles
└── data/               ← folder where PDF and JSON files are stored
```

---

## What needs to be built

Add a **Documents tab** to the existing frontend alongside the current Chat tab. The existing Chat tab must remain completely unchanged.

---

## 1 — Frontend changes (`index.html`, `app.ts`, `styles.css`)

### Tab Switcher

Add a simple tab switcher in the header with two tabs:
- `Chat` — shows the existing chat interface (current default)
- `Documents` — shows the new document management interface

Only one view is visible at a time. The tab switcher should be two simple buttons that toggle between the two views. Match the existing dark UI style.

---

### Documents Tab — Section 1: Upload Area

- A drag and drop zone with the label: `Drop your PDF or JSON files here, or click to select`
- Accepts `.pdf` and `.json` files only
- Supports uploading multiple files at once or one by one
- Shows selected filenames in a simple list below the drop zone before ingestion starts
- A "Process Documents" button below the file list that triggers ingestion
- The button should be disabled if no files are selected

---

### Documents Tab — Section 2: Ingestion Log

- Only visible after clicking "Process Documents"
- Shows a real time step by step log with simple non-technical messages
- Each step appears one by one as the backend streams the response
- Use these exact log messages in this exact order:

```
📂 Documents received and ready for processing
🔍 Extracting financial data from documents
📋 Creating Unified Document Model
✂️ Splitting documents into semantic chunks
💾 Storing chunks in the database
✅ All documents processed — ready to query
```

- Each message should appear with a short visible delay so the user can read them one by one
- After the final message show a green success banner
- After completion automatically reload the document list

---

### Documents Tab — Section 3: Ingested Documents List

- Loads automatically on page load by calling `GET /documents`
- Also reloads after ingestion completes
- If no documents are ingested yet show: `No documents ingested yet`
- Each document is shown as a card with:
  - Company name (bold)
  - Fiscal year
  - File type badge — `PDF` in red, `JSON` in blue (use existing `.source-type` badge styling from `styles.css`)
  - Filename in small muted text
- Card styling should match the existing `.source-item` card styling already in `styles.css`

---

## 2 — Backend changes (`app.py` only)

Add three new endpoints to `app.py`. Do not modify any existing endpoints. Do not modify `ingest.py`, `rag.py`, `semantic.py` or `udm.py`.

---

### Endpoint 1 — File Upload

```
POST /upload
```

- Accepts one or multiple files via multipart form data
- Saves each file to the `/data/` folder
- Resolve the `/data/` folder path relative to `app.py` using `os.path.dirname(__file__)`
- Returns a JSON response with the list of uploaded filenames
- Only accept `.pdf` and `.json` files — reject anything else with a 400 error
- Do not delete or overwrite existing files in `/data/`

---

### Endpoint 2 — Ingestion with Streaming Log

```
POST /ingest
```

- Triggers the full ingestion pipeline by calling `run_ingestion_pipeline()` from `ingest.py`
- Returns a `StreamingResponse` that sends log messages one by one as Server-Sent Events (SSE)
- Stream each log message as a plain text line followed by a newline character `\n`
- Use these exact log messages streamed in this order:

```
📂 Documents received and ready for processing
🔍 Extracting financial data from documents
📋 Creating Unified Document Model
✂️ Splitting documents into semantic chunks
💾 Storing chunks in the database
✅ All documents processed — ready to query
```

- Add a short `asyncio.sleep(0.8)` delay between each message so they appear one by one in the frontend
- After the final message reinitialize the RAG pipeline by calling `create_rag_chain()` and updating the global `rag_pipeline` variable so new documents are immediately queryable in the Chat tab

---

### Endpoint 3 — Document List

```
GET /documents
```

- Returns a list of all documents currently stored in ChromaDB
- Query ChromaDB metadata to get unique documents — deduplicate by filename so the same file is not listed twice
- Each document in the response should have these fields:
  - `company` — company name from chunk metadata
  - `year` — fiscal year from chunk metadata
  - `file` — source filename from chunk metadata
  - `format` — file extension, either `pdf` or `json`
- If ChromaDB is empty or does not exist yet return an empty list — do not throw an error
- Resolve the ChromaDB persist directory the same way as in the existing `rag.py` file

---

## 3 — Important implementation notes

- The existing Chat tab and all its functionality must remain completely unchanged
- The existing `/query` endpoint must remain completely unchanged
- All new CSS styles must follow the existing CSS variable system in `styles.css`:
  - Use `var(--primary)`, `var(--surface)`, `var(--surface-light)`, `var(--text-muted)`, `var(--text-main)`, `var(--green)` etc.
- Document list card styling must match the existing `.source-item` class in `styles.css`
- File type badge styling must match the existing `.source-type` class in `styles.css`
- After editing `app.ts` compile it to `app.js` by running `npx tsc` from inside the `static/` folder
- The server is always started from the project root using:
  ```bash
  PYTHONPATH=backend uvicorn backend.app:app --reload
  ```
- The `data/` folder already exists and contains annual report files — do not delete or modify existing files
- ChromaDB persist directory is `./chroma_db` relative to the project root

---

## 4 — Python dependencies that may need to be added

```bash
pip install python-multipart  # required for FastAPI file uploads
```

---

## 5 — Demo flow this feature enables

For context, this is how the feature will be used during the thesis evaluation:

1. Open the app in the browser
2. Navigate to the **Documents tab**
3. Drag and drop all annual report PDF and JSON files into the upload area
4. Click **"Process Documents"**
5. Watch the ingestion log complete step by step in real time
6. See the document list populate with all ingested documents
7. Switch to the **Chat tab**
8. Ask questions and evaluate the answers against the source documents

---

## 6 — Definition of Done

- [ ] Tab switcher works — clicking Chat shows chat, clicking Documents shows documents tab
- [ ] Files can be uploaded via drag and drop or click to select
- [ ] Only PDF and JSON files are accepted
- [ ] Clicking "Process Documents" streams the ingestion log step by step
- [ ] Each log message appears one by one with a short delay
- [ ] Document list loads on page load from `GET /documents`
- [ ] Document list reloads automatically after ingestion completes
- [ ] Empty state shows "No documents ingested yet" when list is empty
- [ ] Each document card shows company, year, file type badge and filename
- [ ] Chat tab is completely unchanged
- [ ] Server restarts cleanly with `PYTHONPATH=backend uvicorn backend.app:app --reload`
- [ ] `app.ts` is compiled to `app.js` with `npx tsc` from inside `static/`
