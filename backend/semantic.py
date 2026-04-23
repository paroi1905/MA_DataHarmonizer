import time
from typing import List

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.documents import Document
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from udm import UnifiedDocumentModel

load_dotenv()

# --- 1. Semantic Mapping ---
class MappingResult(BaseModel):
    mapped_field: str = Field(description="The standard English field name in the schema.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0 of the mapping.")

# Dynamically extract all float-based financial fields from the UnifiedDocumentModel
VALID_FIELDS = [
    field for field, field_type in UnifiedDocumentModel.__annotations__.items()
    if 'float' in str(field_type).lower()
]

def map_fields(udms: List[UnifiedDocumentModel], mapping_dict: dict) -> List[UnifiedDocumentModel]:
    mapper = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(MappingResult)
    threshold = 0.75
    
    for udm in udms:
        if udm.get("source_format") == "json":
            raw_json = udm["metadata"].get("raw_json", {})
            for ger_key, val in raw_json.items():
                
                # Fast Path: Static Dictionary Mapping
                if ger_key in mapping_dict:
                    english_field = mapping_dict[ger_key]
                    udm[english_field] = float(val)
                    print(f"Static Dict Mapped: {ger_key} -> {english_field}")
                    continue
                    
                # Slow Path: LLM Fallback Mapping
                print(f"LLM Mapping needed for: {ger_key}")
                prompt = f"""
                Map the following German financial term to one of the standardized English fields.
                German Term: '{ger_key}'
                Valid standard fields: {', '.join(VALID_FIELDS)}
                If it does not match any logically, assign it to 'unknown'.
                """
                
                MAX_RETRIES = 4
                for attempt in range(MAX_RETRIES):
                    try:
                        result = mapper.invoke(prompt)
                        if result.mapped_field in VALID_FIELDS and result.confidence >= threshold:
                            udm[result.mapped_field] = float(val)
                            print(f"Mapped: {ger_key} -> {result.mapped_field} ({result.confidence})")
                        break # Break loop on success
                    except Exception as e:
                        if "429" in str(e) or "quota" in str(e).lower() or "rate_limit" in str(e).lower():
                            print(f"Mapping rate limit hit. Sleeping 21s... (Attempt {attempt+1}/{MAX_RETRIES})")
                            time.sleep(21)
                        else:
                            print(f"Error mapping {ger_key}: {e}")
                            break
    return udms

# --- 2. Semantic Chunking ---
class RateLimitedEmbeddings(OpenAIEmbeddings):
    def embed_documents(self, texts, chunk_size=50, **kwargs):
        print(f"Embedding {len(texts)} segments in batches to respect rate limits...")
        results = []
        for i in range(0, len(texts), chunk_size):
            batch = texts[i:i+chunk_size]
            try:
                res = super().embed_documents(batch, chunk_size=chunk_size, **kwargs)
                results.extend(res)
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower() or "rate_limit" in str(e).lower():
                    print("Hit TPM rate limit, sleeping 30 seconds...")
                    time.sleep(30)
                    res = super().embed_documents(batch, chunk_size=chunk_size, **kwargs)
                    results.extend(res)
                else:
                    raise e
            time.sleep(1) # tiny delay between batches
        return results

def chunk_documents(udms: List[UnifiedDocumentModel]):
    embeddings = RateLimitedEmbeddings(chunk_size=50, max_retries=10)
    text_splitter = SemanticChunker(embeddings)
    
    all_chunks = []
    for udm in udms:
        base_metadata = {
            "company": udm["company_name"],
            "year": udm["fiscal_year"],
            "file": udm["source_file"],
            "format": udm["source_format"]
        }
        
        if udm["source_format"] == "pdf":
            docs = text_splitter.create_documents([udm["raw_text"]], metadatas=[base_metadata])
            print(f"Created {len(docs)} chunks for PDF {udm['source_file']}")
            all_chunks.extend(docs)
            
        elif udm["source_format"] == "json":
            content = f"Financial Data for {udm['company_name']} in the year {udm['fiscal_year']}:\n"
            found_data = False
            for field in VALID_FIELDS:
                if udm.get(field) is not None:
                    found_data = True
                    content += f"- {field.replace('_', ' ').title()}: {udm[field]}\n"
                    
            if found_data:
                all_chunks.append(Document(page_content=content, metadata=base_metadata))
                print(f"Created 1 structured chunks for JSON {udm['source_file']}")
            else:
                print(f"No mapped fields for JSON {udm['source_file']}, skipped chunking.")
                
    return all_chunks, embeddings
