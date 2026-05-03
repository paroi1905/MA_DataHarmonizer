#!/usr/bin/env python3
"""
RAGAS Faithfulness Evaluation Script
====================================
This script implements the 4-step RAGAS evaluation process:
1. Run 30 questions through the RAG pipeline and save answers + contexts
2. Run RAGAS on the collected data to get automated scores
3. Save results for manual review (separate step)
4. Generate final evaluation report

Installation: pip install ragas datasets
"""

import json
import os
import time
import sys
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Try to import RAGAS, provide helpful error if not installed
try:
    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy  # Import initialized metric objects
    from ragas.llms import llm_factory
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from datasets import Dataset
    from openai import OpenAI
    RAGAS_AVAILABLE = True
except ImportError as e:
    print(f"ERROR: RAGAS dependencies not installed. Please run:")
    print(f"  pip install ragas datasets openai")
    print(f"Original error: {e}")
    RAGAS_AVAILABLE = False
    sys.exit(1)

from rag import create_rag_chain, get_retriever
from dotenv import load_dotenv

load_dotenv()

# Constants
MAX_RETRIES = 4
RETRY_DELAY = 21  # seconds
FAITHFULNESS_THRESHOLD = 0.85  # 85%


def load_questions() -> List[str]:
    """Load faithfulness questions from JSON file."""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "evaluation", "faithfulness_questions.json")
    
    if not os.path.exists(data_path):
        print(f"ERROR: Questions file not found at {data_path}")
        print("Please ensure data/faithfulness_questions.json exists.")
        sys.exit(1)
    
    with open(data_path, "r", encoding="utf-8") as f:
        questions = json.load(f)
    
    # Use first 40 questions or all if less
    questions = questions[:min(40, len(questions))]
    
    print(f"Loaded {len(questions)} questions for evaluation")
    return questions


def run_query_with_retry(query_func, query: str) -> Dict[str, Any]:
    """Run query with retry logic matching ingest.py (21s delay on 429)."""
    for attempt in range(MAX_RETRIES):
        try:
            return query_func(query)
        except Exception as e:
            error_str = str(e).lower()
            if "429" in str(e) or "quota" in error_str or "rate_limit" in error_str:
                print(f"  Rate limit hit. Sleeping {RETRY_DELAY}s... (Attempt {attempt+1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
            else:
                print(f"  Error processing query: {e}")
                raise e
    
    # If all retries failed
    raise Exception(f"Failed to process query after {MAX_RETRIES} retries")


def collect_ragas_data() -> List[Dict[str, Any]]:
    """
    Step 1: Run questions through RAG pipeline and save answers + contexts.
    Returns list of dictionaries with question, answer, contexts, and sources.
    """
    print("\n" + "="*60)
    print("STEP 1: Collecting answers and contexts")
    print("="*60)
    
    questions = load_questions()
    
    # Initialize RAG components
    print("Initializing RAG pipeline...")
    rag_query = create_rag_chain()
    retriever = get_retriever()
    
    ragas_data = []
    
    for i, question in enumerate(questions, 1):
        print(f"  Processing question {i}/{len(questions)}: '{question[:50]}...'")
        
        try:
            # Get answer from RAG pipeline
            result = run_query_with_retry(rag_query, question)
            
            # Get retrieved contexts directly from retriever for RAGAS
            docs = retriever.invoke(question)
            contexts = [doc.page_content for doc in docs]
            
            ragas_data.append({
                "question": question,
                "answer": result["answer"],
                "contexts": contexts,
                "sources": result["sources"],
                "confidence": result["confidence"]
            })
            
            # Small delay to avoid rate limits
            if i % 5 == 0:
                time.sleep(1)
                
        except Exception as e:
            print(f"  ERROR: Failed to process question '{question[:50]}...': {e}")
            # Add placeholder for failed question
            ragas_data.append({
                "question": question,
                "answer": f"ERROR: {str(e)[:100]}",
                "contexts": [],
                "sources": [],
                "confidence": 0.0
            })
    
    # Save collected data
    output_path = os.path.join(os.path.dirname(__file__), "..", "data", "evaluation", "ragas_evaluation_data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "evaluation_date": datetime.now().isoformat(),
            "total_questions": len(questions),
            "questions": ragas_data
        }, f, indent=2)
    
    print(f"\n✓ Data saved to: {output_path}")
    print(f"  Total questions processed: {len(ragas_data)}")
    
    return ragas_data


def run_ragas_evaluation(ragas_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Step 2: Run RAGAS evaluation on collected data.
    Returns dictionary with faithfulness and answer_relevancy scores.
    """
    print("\n" + "="*60)
    print("STEP 2: Running RAGAS evaluation")
    print("="*60)
    
    # Filter out failed questions
    valid_data = [item for item in ragas_data if item["contexts"] and not item["answer"].startswith("ERROR:")]
    
    if not valid_data:
        print("ERROR: No valid data for RAGAS evaluation")
        return {
            "faithfulness": 0.0,
            "answer_relevancy": 0.0,
            "valid_questions": 0,
            "total_questions": len(ragas_data)
        }
    
    print(f"Running RAGAS on {len(valid_data)} valid questions...")
    
    # Convert to HuggingFace Dataset format
    dataset_dict = {
        "question": [item["question"] for item in valid_data],
        "answer": [item["answer"] for item in valid_data],
        "contexts": [item["contexts"] for item in valid_data]
    }
    
    dataset = Dataset.from_dict(dataset_dict)
    
    # For RAGAS 0.4.3: Use llm_factory and LangChain embeddings with wrapper
    print("  Initializing RAGAS LLM using llm_factory...")
    from openai import OpenAI
    from ragas.llms import llm_factory
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from langchain_openai import OpenAIEmbeddings as LangchainOpenAIEmbeddings
    
    # Create OpenAI client
    openai_client = OpenAI()
    
    # Create RAGAS LLM using llm_factory (required for collections metrics)
    ragas_llm = llm_factory(
        model="gpt-4o",
        client=openai_client,
        temperature=0
    )
    
    # Create LangChain embeddings (has embed_query method) and wrap for RAGAS
    langchain_embeddings = LangchainOpenAIEmbeddings()
    ragas_embeddings = LangchainEmbeddingsWrapper(langchain_embeddings)
    
    # Use imported metric objects and set llm/embeddings attributes
    print("  Configuring RAGAS metrics...")
    # faithfulness and answer_relevancy are already imported as initialized Metric objects
    # We just need to set their llm and embeddings attributes
    faithfulness.llm = ragas_llm
    answer_relevancy.llm = ragas_llm
    answer_relevancy.embeddings = ragas_embeddings
    
    # Run RAGAS evaluation with imported metric objects
    try:
        result = evaluate(
            dataset=dataset,
            metrics=[faithfulness, answer_relevancy]  # Use imported metric objects
        )
        
        # Extract scores - result contains lists of scores per question
        # Calculate average scores
        faithfulness_scores = result["faithfulness"]
        answer_relevancy_scores = result["answer_relevancy"]
        
        # Handle different result formats
        if isinstance(faithfulness_scores, (int, float)):
            # Single score returned
            faithfulness_score = float(faithfulness_scores)
            answer_relevancy_score = float(answer_relevancy_scores)
        elif isinstance(faithfulness_scores, list):
            # List of scores returned - calculate average
            # Filter out nan values for answer_relevancy
            valid_faithfulness_scores = [s for s in faithfulness_scores if not (isinstance(s, float) and (s != s or s is None))]  # Check for nan
            valid_answer_relevancy_scores = [s for s in answer_relevancy_scores if not (isinstance(s, float) and (s != s or s is None))]  # Check for nan
            
            if not valid_faithfulness_scores:
                faithfulness_score = 0.0
                print("  Warning: All faithfulness scores are nan/None")
            else:
                faithfulness_score = float(sum(valid_faithfulness_scores)) / len(valid_faithfulness_scores)
            
            if not valid_answer_relevancy_scores:
                answer_relevancy_score = 0.0
                print("  Warning: All answer_relevancy scores are nan/None")
            else:
                answer_relevancy_score = float(sum(valid_answer_relevancy_scores)) / len(valid_answer_relevancy_scores)
        else:
            # Unknown format
            raise ValueError(f"Unexpected result format: faithfulness_scores type={type(faithfulness_scores)}")
        
        print(f"✓ RAGAS evaluation completed")
        print(f"  Faithfulness: {faithfulness_score:.3f} ({faithfulness_score*100:.1f}%)")
        print(f"  Answer Relevancy: {answer_relevancy_score:.3f} ({answer_relevancy_score*100:.1f}%)")
        print(f"  Questions evaluated: {len(faithfulness_scores)}")
        
        return {
            "faithfulness": faithfulness_score,
            "answer_relevancy": answer_relevancy_score,
            "valid_questions": len(valid_data),
            "total_questions": len(ragas_data)
        }
        
    except Exception as e:
        print(f"ERROR: RAGAS evaluation failed: {e}")
        return {
            "faithfulness": 0.0,
            "answer_relevancy": 0.0,
            "valid_questions": len(valid_data),
            "total_questions": len(ragas_data),
            "error": str(e)
        }


def save_final_results(ragas_scores: Dict[str, Any]) -> None:
    """
    Step 3: Save final results in clean JSON format for thesis.
    """
    print("\n" + "="*60)
    print("STEP 3: Saving final results")
    print("="*60)
    
    # Determine if threshold is passed
    passed = ragas_scores["faithfulness"] >= FAITHFULNESS_THRESHOLD
    
    results = {
        "evaluation_date": datetime.now().isoformat(),
        "faithfulness": ragas_scores["faithfulness"],
        "answer_relevancy": ragas_scores.get("answer_relevancy", 0.0),
        "threshold": FAITHFULNESS_THRESHOLD,
        "passed": passed,
        "valid_questions": ragas_scores.get("valid_questions", 0),
        "total_questions": ragas_scores.get("total_questions", 0),
        "notes": "Manual review: Check ragas_evaluation_data.json for question-level details"
    }
    
    # Save results
    results_path = os.path.join(os.path.dirname(__file__), "..", "data", "evaluation", "ragas_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"✓ Final results saved to: {results_path}")
    print(f"\nRESULTS SUMMARY:")
    print(f"  Faithfulness: {results['faithfulness']:.3f} ({results['faithfulness']*100:.1f}%)")
    print(f"  Answer Relevancy: {results['answer_relevancy']:.3f} ({results['answer_relevancy']*100:.1f}%)")
    print(f"  Threshold: {results['threshold']} (85%)")
    print(f"  Passed: {'YES' if results['passed'] else 'NO'}")
    print(f"  Valid questions: {results['valid_questions']}/{results['total_questions']}")
    
    # Manual review instructions
    print(f"\nMANUAL REVIEW INSTRUCTIONS:")
    print(f"  1. Review data/ragas_evaluation_data.json for detailed question-level data")
    print(f"  2. Check 10 random questions for faithfulness and relevance")
    print(f"  3. Compare with RAGAS scores above")
    print(f"  4. Include agreement percentage in thesis")


def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("RAGAS FAITHFULNESS EVALUATION")
    print("="*60)
    print("This script follows the 4-step evaluation process:")
    print("1. Collect answers and contexts from RAG pipeline")
    print("2. Run RAGAS evaluation (faithfulness + answer_relevancy)")
    print("3. Save results for manual review")
    print("4. Generate final report")
    print("\nNote: Manual validation is a separate step after script completion.")
    
    try:
        # Step 1: Collect data
        ragas_data = collect_ragas_data()
        
        # Step 2: Run RAGAS evaluation
        ragas_scores = run_ragas_evaluation(ragas_data)
        
        # Step 3: Save final results
        save_final_results(ragas_scores)
        
        print("\n" + "="*60)
        print("EVALUATION COMPLETE")
        print("="*60)
        print("Next steps:")
        print("1. Manually review data/ragas_evaluation_data.json")
        print("2. Check 10 random questions for accuracy")
        print("3. Include RAGAS scores in thesis evaluation section")
        
    except Exception as e:
        print(f"\nERROR: Evaluation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()