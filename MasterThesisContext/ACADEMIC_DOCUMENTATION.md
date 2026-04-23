# Academic Documentation: Retrieval-Augmented Generation (RAG) Architecture for Financial Data Ingestion

## 1. Introduction and Objectives
The prototype developed for this thesis addresses the challenge of structural heterogeneity in corporate financial reporting. Annual reports and financial disclosures—such as those published by Austrian corporations—are fundamentally asymmetrical, existing as highly unstructured PDF texts or deeply nested, idiosyncratic JSON structures. The primary objective of this system is to dynamically normalize these disparate data sources into a standardized, unified schema (the Unified Document Model) and subsequently vectorize the semantic data to enable LLM-based Retrieval-Augmented Generation (RAG) with high accuracy and low hallucination latency.

## 2. High-Level System Architecture
The system adopts a modular, domain-driven architecture utilizing a decoupling strategy between the data pipeline, the semantic intelligence layer, the retrieval engine, and the client interface. The backend utilizes Python via the FastAPI framework, while the semantic processes integrate LangChain abstractions alongside OpenAI's embedding and generative models. The client interface is a compiled Vanilla TypeScript application, eliminating front-end framework overhead.

---

## 3. Backend Module Implementation

The backend logic is strictly segregated into five independent Python modules designed to enforce single-responsibility principles.

### 3.1 Data Schema Normalization (`udm.py`)
To prevent data contamination, the data structure must be heavily regulated prior to insertion into the vector space. `udm.py` defines the **Unified Document Model (UDM)** via Python's `TypedDict`. This module acts as the central schema registry, explicitly typing financial Key Performance Indicators (KPIs) such as `revenue`, `gross_profit`, and `total_assets` as `Optional[float]`. Consequently, regardless of the source's native structure (PDF vs. JSON), the downstream pipeline processes a mathematically guaranteed uniform data type.

### 3.2 The Ingestion Orchestrator (`ingest.py`)
`ingest.py` controls the extraction and transformation heuristics of raw data inputs. 
- **PDF Processing Component:** Evaluates flat textual documents via `PyPDFLoader`, extracting raw string data for downstream semantic analysis.
- **JSON Recursion Component:** Utilizes a custom recursive traversal algorithm (`flatten_financial_data()`) designed to traverse indeterminate hierarchical document structures dynamically. It locates standard key-value pairs (e.g., parsing nodes containing `"name"` and `"value"` attributes) and flattens the multidimensional array into a single-depth dictionary.
- **Surgical Ingestion Wrapper (`ingest_single_file`):** In order to mitigate heavy computational overhead, this wrapper handles targeted insertion. By computing a specified user upload, it vectors a single file directly into the memory node instead of recalculating the entire dataset directory.

### 3.3 The Semantic Analysis Layer (`semantic.py`)
The semantic layer handles linguistic harmonization and spatial chunking.
- **Dynamic Field Mapping (`map_fields`):** Because Austrian firms use disparate lexical phrasing to describe identical KPIs (e.g., *Gesamtkapital* versus *Total Assets*), this function aligns terminologies into the UDM format. 
  - *Heuristic Fast-Path:* The algorithm first checks a static dictionary (`mapping_dictionary.json`) to invoke low-latency $O(1)$ heuristic mapping.
  - *LLM Fallback Node:* Should the lexical item not exist in the dictionary, the algorithm delegates the mapping to an LLM `ChatOpenAI` endpoint. Utilizing strict prompt constraints, the AI maps the unknown German phrasing to the standard UDM annotations dynamically extracted via Python's built-in `typing` module (`UnifiedDocumentModel.__annotations__`).
- **Semantic Text Segmentation (`chunk_documents`):** Instead of utilizing arbitrary character-count truncation, the documents are segmented heuristically using LangChain's `SemanticChunker`. This logic analyzes text clusters via cosine similarity and only triggers a "split" when a mathematical deviation indicates a shift in conversational context.

### 3.4 Retrieval & Generation Engine (`rag.py`)
This module initializes the vector space and establishes the RAG querying architecture.
- **Vector Space Modeling:** Employs ChromaDB as the underlying persistent vector store, mapping textual significance across high-dimensional coordinates utilizing the `RateLimitedEmbeddings` helper (an error-handling wrapper designed to combat HTTP 429 API rate limits using an exponential backoff methodology).
- **The Generative Chain (`create_rag_chain`):** Uses an asynchronous retriever to perform a K-Nearest Neighbors ($k=4$) search algorithm to fetch the mathematically closest matching semantic chunks in the ChromaDB relative to the user query. The retrieved chunks are forcefully injected into a constrained LangChain template prompt to ground the generative AI (e.g. GPT-4o-mini), strictly reducing epistemic hallucinations and forcing the model to cite specific file names and fiscal years corresponding to the injected spatial chunks.

### 3.5 Client-Server Gateway (`app.py`)
This script represents the application's RESTful API edge. Leveraging the asynchronous properties of ASGI servers (`FastAPI`), it initializes the `/query` JSON endpoint (to process frontend inference requests) and the `/upload` multimedia endpoint (which parses incoming file bytes, writes them securely to local storage, and invokes `ingest.py` for asynchronous processing).

---

## 4. Frontend Client Architecture

The frontend (`/static/`) serves as the presentational layer designed using a minimalist architectural paradigm completely independent of virtual-DOM libraries like React or Vue. 

- **Application Logic (`app.ts`):** Authored in strict TypeScript, this module intercepts browser Document Object Model (DOM) events. It manages asynchronous HTTP calls via the `fetch` API, coordinates loading UI states, and dynamically compiles responses—displaying AI context alongside exact retrieval citations embedded with a calculated algorithmic Confidence Score inline.
- **Cascading Stylings (`styles.css`):** Implements modern human-computer interaction (HCI) concepts focusing on cognitive load reduction, employing CSS Flexbox models to structure a side-by-side dashboard alongside a "Glassmorphism" aesthetic schema.
- **Document Structure (`index.html`):** Represents the static markup boundary integrating semantic web tags alongside a visually distinct file-ingestion dropzone module.

## 5. Conclusion
By cleanly decoupling raw data normalization, semantic similarity chunking, heuristic translation fallbacks, and the generative modeling constraints, the prototype successfully synthesizes a methodology for handling mathematically disparate financial ledgers. This architecture directly addresses the academic obstacles surrounding LLM hallucinations by forcing deterministic routing constraints over an unstructured data retrieval model.
