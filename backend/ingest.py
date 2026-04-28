import os
import re
import json
from typing import List

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader

from udm import UnifiedDocumentModel
from semantic import map_fields, chunk_documents
from rag import populate_vectorstore

load_dotenv()

# --- 1. Loaders ---
def load_pdf(file_path:str) -> UnifiedDocumentModel:
    print(f"Loading PDF: {file_path}")
    docs = PyPDFLoader(file_path).load()
    text = "\n".join([d.page_content for d in docs])
    return {
        "company_name": "", "fiscal_year": 0, "source_format": "pdf",
        "source_file": os.path.basename(file_path), "raw_text": text,
        "revenue": None, "gross_profit": None, "operating_profit": None,
        "net_profit": None, "interest_expense": None, "tax_expense": None,
        "depreciation": None, "total_assets": None, "current_assets": None,
        "fixed_assets": None, "total_liabilities": None, "equity": None,
        "cash": None, "metadata": {}
    }

def load_mapping_dictionary():
    dict_path = os.path.join(os.path.dirname(__file__), "..", "data", "mapping_dictionary.json")
    if os.path.exists(dict_path):
        with open(dict_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

EXCLUDE_TERMS = [
    "RECHNUNGSABGRENZUNG",
    "LATENTE",
    "INVESTITIONSZUSCHUSS",
    "INVESTITIONSZUSCHUESSE"
]

def flatten_financial_data(data, mapping_dict):
    """Recursively search for 'name' and 'value' attributes in the nested JSON"""
    flat = {}
    if isinstance(data, dict):
        for key_field in ["name", "title"]:
            if key_field in data and "value" in data and isinstance(data["value"], (int, float)):
                key = data[key_field]
                if any(excl in key.upper() for excl in EXCLUDE_TERMS):
                    continue
                if key in mapping_dict or any(term in key.upper() for term in mapping_dict.keys()):
                    flat[key] = data["value"]
            
        for k, v in data.items():
            flat.update(flatten_financial_data(v, mapping_dict))
    elif isinstance(data, list):
        for item in data:
            flat.update(flatten_financial_data(item, mapping_dict))
    return flat

def load_json(file_path: str, mapping_dict: dict) -> UnifiedDocumentModel:
    print(f"Loading JSON: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    flat_data = flatten_financial_data(data, mapping_dict)
    return {
        "company_name": "", "fiscal_year": 0, "source_format": "json",
        "source_file": os.path.basename(file_path), "raw_text": None,
        "revenue": None, "gross_profit": None, "operating_profit": None,
        "net_profit": None, "interest_expense": None, "tax_expense": None,
        "depreciation": None, "total_assets": None, "current_assets": None,
        "fixed_assets": None, "total_liabilities": None, "equity": None,
        "cash": None, "metadata": {"raw_json": flat_data}
    }

# --- 2. Enqueue Files ---
def load_all_documents(data_dir: str, mapping_dict: dict) -> List[UnifiedDocumentModel]:
    udms = []
    if not os.path.exists(data_dir):
        return udms
    for root, _, files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".pdf"):
                udms.append(load_pdf(file_path))
            elif file.endswith(".json"):
                udms.append(load_json(file_path, mapping_dict))
    return udms

def enrich_metadata(udms: List[UnifiedDocumentModel]) -> List[UnifiedDocumentModel]:
    for udm in udms:
        filename = udm["source_file"]
        company, year = "Unknown", 0
        match = re.search(r'([A-Za-z0-9_]+)_(\d{4})\.(pdf|json)$', filename)
        if match:
            raw_company = match.group(1).replace("_", " ")
            company = " ".join([word.capitalize() for word in raw_company.split(" ")])
            company = re.sub(r'^Jab\s+', '', company, flags=re.IGNORECASE)
            year = int(match.group(2))
        udm["company_name"] = company
        udm["fiscal_year"] = year
    return udms

# --- Main Ingestion Logic Orchestrator ---
def run_ingestion_pipeline():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    print(f"--- Starting Full Ingestion Pipeline ---")
    
    mapping_dict = load_mapping_dictionary()
    print(f"Loaded static mapping dictionary with {len(mapping_dict)} known terms.")
    
    print("\nStep 1: Extracting documents...")
    udms = load_all_documents(data_dir, mapping_dict)
    
    print("\nStep 2: Enriching Metadata...")
    udms = enrich_metadata(udms)
    
    print("\nStep 3: Harmonizing schemas via Semantic Mapper...")
    udms = map_fields(udms, mapping_dict)
    
    print("\nStep 4: Chunking Documents Semantically...")
    chunks, embeddings = chunk_documents(udms)
    
    print("\nStep 5: Vectorizing into Chroma Database...")
    populate_vectorstore(chunks, embeddings)
    
    print("\n✅ Ingestion complete! The data is now available for querying.")


def ingest_single_file(file_path: str):
    print(f"--- Starting Single File Ingestion: {file_path} ---")
    mapping_dict = load_mapping_dictionary()
    
    udms = []
    if file_path.endswith(".pdf"):
        udms.append(load_pdf(file_path))
    elif file_path.endswith(".json"):
        udms.append(load_json(file_path, mapping_dict))
    else:
        raise ValueError("Unsupported file format")

    udms = enrich_metadata(udms)
    udms = map_fields(udms, mapping_dict)
    chunks, embeddings = chunk_documents(udms)
    
    if chunks:
        populate_vectorstore(chunks, embeddings)
        print(f"✅ {os.path.basename(file_path)} vectorized!")
    else:
        print(f"⚠️ No semantic chunks created for {os.path.basename(file_path)}")

if __name__ == "__main__":
    run_ingestion_pipeline()
