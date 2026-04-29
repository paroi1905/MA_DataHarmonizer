import os
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from semantic import RateLimitedEmbeddings

load_dotenv()

# --- 1. Vector Store Management ---
def get_persist_directory() -> str:
    return os.getenv("CHROMA_PERSIST_DIR", os.path.join(os.path.dirname(__file__), "..", "chroma_db"))

def get_vectorstore(embeddings_model=None):
    if embeddings_model is None:
        embeddings_model = RateLimitedEmbeddings(chunk_size=50)
    persist_directory = get_persist_directory()
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings_model)

def populate_vectorstore(chunks, embeddings_model):
    """Saves semantic chunks to the Chroma DB"""
    vectorstore = get_vectorstore(embeddings_model)
    vectorstore.add_documents(chunks)
    vectorstore.persist()
    return vectorstore

# --- 2. RAG Retrieval & Generation ---
SYSTEM_PROMPT = """
You are a precise financial analyst assistant.
Your task is to answer the user's question USING ONLY the provided context.
If you cannot find the answer in the context or if you are unsure, you MUST state explicitly:
"I cannot answer this question based on the provided documents."

NEVER hallucinate or use outside knowledge. Address the user directly and professionally.

Context:
{context}
"""

def format_docs(docs):
    formatted = []
    for doc in docs:
        c = doc.metadata.get("company", "Unknown")
        y = doc.metadata.get("year", "Unknown")
        f = doc.metadata.get("file", "Unknown")
        formatted.append(f"[Source: {c}, {y}, {f}]\n{doc.page_content}")
    return "\n\n".join(formatted)

def get_retriever(company_filter=None):
    """Returns the retriever for evaluation purposes"""
    vectorstore = get_vectorstore()
    search_kwargs = {"k": 4}
    if company_filter:
        search_kwargs["filter"] = {"company": company_filter}
    return vectorstore.as_retriever(search_kwargs=search_kwargs)

def detect_company(query: str) -> str | None:
    known = {"Bitpanda": "Bitpanda",
             "Maresi": "Maresi",
             "Senna": "Senna",
             "Smarter Ecommerce": "Smarter Ecommerce Gmbh"
            }
    for partial_name, stored_name in known.items():
        if partial_name.lower() in query.lower():
            return stored_name
    return None

def create_rag_chain():
    """Builds the end-to-end RAG workflow (Retriever -> Prompt -> LLM)"""
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    def run_query(query: str) -> dict:
        company = detect_company(query)
        retriever = get_retriever(company_filter=company)
        
        # Retrieve context
        docs = retriever.invoke(query)
        context_str = format_docs(docs)
        
        # Generate Answer
        answer = chain.invoke({"context": context_str, "question": query})
        
        # Extract metadata for citations
        # Only show sources if LLM actually answered the question
        cannot_answer_phrases = [
            "cannot answer",
            "can't answer",
            "not able to answer",
            "no information",
            "not found in"
        ]

        if any(phrase in answer.lower() for phrase in cannot_answer_phrases):
            unique_sources = []
        else:
            sources = []
            for d in docs:
                sources.append({
                    "company": d.metadata.get("company", "Unknown"),
                    "year": d.metadata.get("year", 0),
                    "file": d.metadata.get("file", "Unknown"),
                })
            unique_sources = [dict(t) for t in {tuple(s.items()) for s in sources}]

        return {
            "answer": answer,
            "sources": unique_sources,
            "confidence": 0.9,  # Metric mock
            "contexts": [doc.page_content for doc in docs]  # For RAGAS evaluation
        }
        
    return run_query
