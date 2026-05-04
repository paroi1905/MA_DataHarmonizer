import json
import os
import time

BASELINE_SECONDS = 151200  # 42 hours mean baseline
CONSERVATIVE_BASELINE = 72000  # 20 hours conservative baseline
THRESHOLD = 75.0
TIME_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "evaluation", "ingestion_time.json")

def load_ingestion_time() -> float | None:
    if os.path.exists(TIME_LOG_PATH):
        with open(TIME_LOG_PATH, "r") as f:
            data = json.load(f)
            return data.get("artifact_seconds")
    return None

def eval_processing_time():
    print("\n" + "="*50)
    print("EVALUATION 1: Controlled Experiment (Time Reduction)")
    print("="*50)

    artifact_seconds = load_ingestion_time()

    if artifact_seconds is None:
        print("ERROR: No ingestion time found.")
        print("Please run the ingestion pipeline first:")
        print("  rm -rf chroma_db/")
        print("  python backend/ingest.py")
        return False

    print(f"Artifact Processing Time:      {artifact_seconds:.1f} seconds")
    print(f"Average Manual Baseline:          {BASELINE_SECONDS} seconds (42 hours)")
    print(f"Conservative Manual Baseline:  {CONSERVATIVE_BASELINE} seconds (20 hours)")

    reduction_mean = ((BASELINE_SECONDS - artifact_seconds) / BASELINE_SECONDS) * 100
    reduction_conservative = ((CONSERVATIVE_BASELINE - artifact_seconds) / CONSERVATIVE_BASELINE) * 100

    print(f"\nTime Reduction (average):         {reduction_mean:.2f}%")
    print(f"Time Reduction (conservative): {reduction_conservative:.2f}%")
    print(f"Threshold:                     >{THRESHOLD}%")

    success = reduction_mean > THRESHOLD and reduction_conservative > THRESHOLD
    print(f"\nSuccess (both >75%):           {'PASS' if success else 'FAIL'}")
    return success

if __name__ == "__main__":
    eval_processing_time()