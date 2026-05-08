import json
import os

BASELINE_P1_SECONDS = 72000    # Participant 1: 5h per pair × 4 = 20h
BASELINE_P2_SECONDS = 230400   # Participant 2: 16h per pair × 4 = 64h
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

    reduction_p1 = ((BASELINE_P1_SECONDS - artifact_seconds) / BASELINE_P1_SECONDS) * 100
    reduction_p2 = ((BASELINE_P2_SECONDS - artifact_seconds) / BASELINE_P2_SECONDS) * 100

    print(f"Artifact Processing Time:          {artifact_seconds:.1f} seconds")
    print(f"Participant 1 Baseline (P1):       {BASELINE_P1_SECONDS} seconds (20 hours)")
    print(f"Participant 2 Baseline (P2):       {BASELINE_P2_SECONDS} seconds (64 hours)")
    print(f"Threshold:                         >{THRESHOLD}%")
    print(f"\nTime Reduction vs P1 (conservative): {reduction_p1:.2f}%")
    print(f"Time Reduction vs P2 (upper bound):  {reduction_p2:.2f}%")

    success = reduction_p1 > THRESHOLD and reduction_p2 > THRESHOLD
    print(f"\nSuccess (both >{THRESHOLD}%):          {'PASS' if success else 'FAIL'}")
    return success

if __name__ == "__main__":
    eval_processing_time()