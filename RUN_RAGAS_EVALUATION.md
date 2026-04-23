# Run RAGAS Evaluation - Quick Start

## Prerequisites

1. Ensure `.env` file has `OPENAI_API_KEY` set
2. Ensure RAG pipeline is working (test with `fastapi dev backend/app.py`)

## Installation

```bash
pip install ragas datasets openai
```

## Run Evaluation

```bash
cd /Users/patrick/MA_MVP_Prototype_TEST
python -m backend.evaluate_ragas
```

## What Happens

1. **Step 1**: Loads 30 questions from `data/faithfulness_questions.json`
2. **Step 2**: Runs each through your RAG pipeline (with 21s retry on 429 errors)
3. **Step 3**: Evaluates with RAGAS (faithfulness + answer_relevancy metrics)
4. **Step 4**: Saves results to `data/ragas_results.json`

## Output Files

- `data/ragas_evaluation_data.json`: Questions + answers + contexts for manual review
- `data/ragas_results.json`: Final scores for thesis:
  ```json
  {
    "faithfulness": 0.87,
    "answer_relevancy": 0.92,
    "threshold": 0.85,
    "passed": true
  }
  ```

## For Thesis

Include in evaluation section:

- RAGAS faithfulness score (from `ragas_results.json`)
- RAGAS answer relevancy score
- Manual agreement percentage (check 10 random questions)
- Pass/fail against 85% threshold

## Troubleshooting

- **API errors**: Script retries 4 times with 21s delays (matches `ingest.py`)
- **Missing dependencies**: Run `pip install ragas datasets openai`
- **No questions**: Ensure `data/faithfulness_questions.json` exists

The script is now fixed and ready to run!
