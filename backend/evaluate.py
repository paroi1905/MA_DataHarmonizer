import json
import os
import time
import sys

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

sys.path.append(os.path.dirname(__file__))
from ingest import load_all_documents, load_mapping_dictionary

load_dotenv()

# --- 1. Controlled Experiment Evaluation ---
def eval_controlled_experiment():
    print("\n" + "="*50)
    print("EVALUATION 1: Controlled Experiment (Time Reduction)")
    print("="*50)
    
    baseline_hours = 42 
    baseline_seconds = baseline_hours * 3600
    
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    
    start_time = time.time()
    print("Running document extraction phase (simulation)...")
    mapping_dict = load_mapping_dictionary()
    udms = load_all_documents(data_dir, mapping_dict)
    end_time = time.time()
    
    artifact_seconds = end_time - start_time
    time_reduction_percentage = ((baseline_seconds - artifact_seconds) / baseline_seconds) * 100
    
    print(f"Manual Baseline: {baseline_seconds}s")
    print(f"Artifact Extraction Time: {artifact_seconds:.2f}s")
    print(f"Time Reduction: {time_reduction_percentage:.4f}%")
    
    success = time_reduction_percentage > 75.0
    print(f"Success (>75% reduction required): {success}")
    return success

# --- 2. Semantic Mapping Evaluation ---
class MappingResult(BaseModel):
    mapped_field: str = Field(description="Standard English field name.")
    confidence: float = Field(description="Confidence between 0.0 and 1.0.")

def eval_semantic_mapping():
    print("\n" + "="*50)
    print("EVALUATION 2: Semantic Mapping (Precision & Recall)")
    print("="*50)
    
    # Use the new 50-term gold standard dataset
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "evaluation", "gold_standard_50_terms.json")
    if not os.path.exists(data_path):
        print(f"ERROR: Gold standard dataset not found at {data_path}")
        print("Please create the 50-term dataset first.")
        return False
    
    with open(data_path, "r") as f:
        ground_truth = json.load(f)
    
    print(f"Loaded {len(ground_truth)} terms from gold standard dataset")
    
    # Get valid UDM fields dynamically
    from udm import UnifiedDocumentModel
    valid_fields = list(UnifiedDocumentModel.__annotations__.keys())
    # Remove non-financial fields
    non_financial_fields = ["company_name", "fiscal_year", "source_format", "source_file", "raw_text", "metadata"]
    valid_fields = [f for f in valid_fields if f not in non_financial_fields]
    valid_fields.append("unknown")  # Add unknown as valid response
    
    print(f"Valid UDM fields for mapping: {valid_fields}")
    
    mapper = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(MappingResult)
    
    # Initialize counters
    true_positives = false_positives = false_negatives = 0
    category_results = {}
    difficulty_results = {"easy": {"tp": 0, "fp": 0, "fn": 0}, 
                         "medium": {"tp": 0, "fp": 0, "fn": 0}, 
                         "hard": {"tp": 0, "fp": 0, "fn": 0}}
    
    print("\nStarting semantic mapping evaluation...")
    
    for i, item in enumerate(ground_truth, 1):
        ger = item["german"]
        expected = item["english"]
        category = item["category"]
        difficulty = item["difficulty"]
        
        # Initialize category counter if needed
        if category not in category_results:
            category_results[category] = {"tp": 0, "fp": 0, "fn": 0}
        
        prompt = f"Map the German financial term '{ger}' to one of these standardized English field names: {valid_fields}. If the term doesn't match any field, return 'unknown'."
        
        try:
            res = mapper.invoke(prompt)
            predicted = res.mapped_field.lower()  # Normalize to lowercase
            
            # Update counters
            if predicted == expected:
                true_positives += 1
                category_results[category]["tp"] += 1
                difficulty_results[difficulty]["tp"] += 1
            elif predicted == "unknown" and expected == "unknown":
                true_positives += 1  # Correctly identified as unknown
                category_results[category]["tp"] += 1
                difficulty_results[difficulty]["tp"] += 1
            elif predicted == "unknown":
                false_negatives += 1  # Should have mapped but didn't
                category_results[category]["fn"] += 1
                difficulty_results[difficulty]["fn"] += 1
            else:
                false_positives += 1  # Wrong mapping
                category_results[category]["fp"] += 1
                difficulty_results[difficulty]["fp"] += 1
            
            # Progress indicator
            if i % 10 == 0:
                print(f"  Processed {i}/{len(ground_truth)} terms...")
                
        except Exception as e:
            print(f"Error mapping '{ger}': {e}")
            false_negatives += 1  # Count as failure
            category_results[category]["fn"] += 1
            difficulty_results[difficulty]["fn"] += 1
    
    # Calculate overall metrics
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print("\n" + "-"*50)
    print("OVERALL RESULTS:")
    print(f"Total Terms: {len(ground_truth)}")
    print(f"True Positives: {true_positives}")
    print(f"False Positives: {false_positives}")
    print(f"False Negatives: {false_negatives}")
    print(f"Precision: {precision*100:.1f}% (Threshold: >85%)")
    print(f"Recall: {recall*100:.1f}% (Threshold: >80%)")
    print(f"F1 Score: {f1_score*100:.1f}%")
    
    # Print category breakdown
    print("\nCATEGORY BREAKDOWN:")
    for category, counts in category_results.items():
        cat_total = counts["tp"] + counts["fp"] + counts["fn"]
        if cat_total > 0:
            cat_precision = counts["tp"] / (counts["tp"] + counts["fp"]) if (counts["tp"] + counts["fp"]) > 0 else 0
            cat_recall = counts["tp"] / (counts["tp"] + counts["fn"]) if (counts["tp"] + counts["fn"]) > 0 else 0
            print(f"  {category}: {counts['tp']}/{cat_total} correct (P: {cat_precision*100:.1f}%, R: {cat_recall*100:.1f}%)")
    
    # Print difficulty breakdown
    print("\nDIFFICULTY BREAKDOWN:")
    for difficulty, counts in difficulty_results.items():
        diff_total = counts["tp"] + counts["fp"] + counts["fn"]
        if diff_total > 0:
            diff_precision = counts["tp"] / (counts["tp"] + counts["fp"]) if (counts["tp"] + counts["fp"]) > 0 else 0
            diff_recall = counts["tp"] / (counts["tp"] + counts["fn"]) if (counts["tp"] + counts["fn"]) > 0 else 0
            print(f"  {difficulty}: {counts['tp']}/{diff_total} correct (P: {diff_precision*100:.1f}%, R: {diff_recall*100:.1f}%)")
    
    success = precision > 0.85 and recall > 0.80
    print(f"\nSuccess (Precision >85% AND Recall >80%): {success}")
    return success

def run_all_evaluations():
    print("Starting Thesis Master Evaluations...\n")
    s1 = eval_controlled_experiment()
    s2 = eval_semantic_mapping()
    
    print("\n" + "*"*50)
    print("FINAL EVALUATION SUMMARY")
    print(f"1. Controlled Experient : {'PASS' if s1 else 'FAIL'}")
    print(f"2. Semantic Mapping     : {'PASS' if s2 else 'FAIL'}")
    print("*"*50)
    
    if s1 and s2:
        print("ALL SUCCESS CRITERIA MET. PROTOTYPE VALIDATED.")
    else:
        print("SOME CRITERIA FAILED. REVIEW LOGS.")

if __name__ == "__main__":
    run_all_evaluations()
