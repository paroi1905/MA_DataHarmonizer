# RAGAS Faithfulness Evaluation

This document describes the RAGAS-based faithfulness evaluation for the Financial RAG Assistant.

## Overview

The RAGAS (Retrieval-Augmented Generation Assessment) framework provides automated, reference-free evaluation of RAG systems. This implementation follows a 4-step process:

1. **Collect answers and contexts** - Run 30 questions through the RAG pipeline
2. **Run RAGAS evaluation** - Automated scoring of faithfulness and answer relevancy
3. **Manual review** - Human validation of 10 random questions (separate step)
4. **Report results** - Include scores and manual agreement in thesis

## Installation

First, install the required dependencies:

```bash
pip install ragas datasets openai
```

These packages are already added to `requirements.txt` but need to be installed separately.

## Files Created

### Script Files

- `backend/evaluate_ragas.py` - Main evaluation script

### Data Files (created during execution)

- `data/ragas_evaluation_data.json` - Questions, answers, and contexts for manual review
- `data/ragas_results.json` - Final RAGAS scores and pass/fail status

## Usage

Run the evaluation script from the project root:

```bash
cd /Users/patrick/MA_MVP_Prototype_TEST
python -m backend.evaluate_ragas
```

## What the Script Does

### Step 1: Data Collection

- Loads 30 questions from `data/faithfulness_questions.json`
- Runs each through the RAG pipeline with retry logic (21s delay on 429 errors)
- Saves questions, answers, contexts, and sources to `ragas_evaluation_data.json`

### Step 2: RAGAS Evaluation

- Converts data to HuggingFace Dataset format
- Creates RAGAS native `OpenAIEmbeddings` instance (independent of custom RateLimitedEmbeddings)
- Creates OpenAI client and uses RAGAS native `llm_factory` to create LLM instance
- Runs RAGAS with two metrics from `ragas.metrics.collections`:
  - `Faithfulness(llm=ragas_llm)` - Measures if answers are grounded in retrieved contexts
  - `AnswerRelevancy(llm=ragas_llm, embeddings=ragas_embeddings)` - Measures if answers directly address the questions (requires embeddings)
- Calculates scores on 0-1 scale (0.85 = 85%)

### Step 3: Results Saving

- Saves clean JSON with:
  - `faithfulness` score (0-1)
  - `answer_relevancy` score (0-1)
  - `threshold` (0.85 = 85%)
  - `passed` (true/false based on threshold)
  - Question counts for validation

### Step 4: Manual Review (Separate Step)

- Review `ragas_evaluation_data.json` manually
- Check 10 random questions for faithfulness and relevance
- Calculate agreement percentage between RAGAS and human judgment
- Include in thesis: RAGAS scores + manual agreement percentage

## Integration with Thesis

### In Evaluation Section (Section 3):

```
The faithfulness evaluation employed the RAGAS (Retrieval-Augmented Generation Assessment)
framework for automated, reference-free evaluation. Thirty financial questions were processed
through the RAG pipeline, with answers and retrieved contexts saved for analysis. RAGAS
calculated a faithfulness score of [INSERT FAITHFULNESS SCORE] and an answer relevancy score
of [INSERT ANSWER RELEVANCY SCORE] on a 0-1 scale. Manual review of ten randomly selected
questions showed [INSERT AGREEMENT PERCENTAGE]% agreement with RAGAS judgments. The artifact
[PASSED/FAILED] the 85% faithfulness threshold required for financial applications.
```

### Results JSON Structure:

```json
{
  "evaluation_date": "2026-04-19T10:30:00",
  "faithfulness": 0.87,
  "answer_relevancy": 0.92,
  "threshold": 0.85,
  "passed": true,
  "valid_questions": 30,
  "total_questions": 30,
  "notes": "Manual review: Check ragas_evaluation_data.json for question-level details"
}
```

## Key Features

### Consistent Error Handling

- Same retry logic as `ingest.py` (21s delay, 4 retries on 429 errors)
- Graceful handling of API rate limits
- Continues evaluation even if some questions fail

### Clean Architecture

- `rag.py` modified with `get_retriever()` function for reuse
- No changes to original `eval_faithfulness()` in `evaluate.py`
- Separate script avoids conflicts with existing evaluation

### Practical Output

- JSON files ready for thesis inclusion
- Clear separation between automated and manual steps
- Detailed data for manual validation

## Comparison with Original Evaluation

### Original (`eval_faithfulness()` in `evaluate.py`):

- Manual/semi-automated scoring
- Simple heuristic: `has_sources and confidence > 0.7`
- Limited to 30-40 questions due to manual effort
- No answer relevancy measurement

### RAGAS (`evaluate_ragas.py`):

- Fully automated scoring
- Standardized metrics: faithfulness + answer_relevancy
- Scalable to hundreds of questions
- Reference-free (no ground truth needed)
- Enables continuous evaluation

## Next Steps After Running

1. **Run the script**: `python -m backend.evaluate_ragas`
2. **Check results**: Review `data/ragas_results.json` for scores
3. **Manual validation**: Open `data/ragas_evaluation_data.json` and check 10 random questions
4. **Calculate agreement**: Note how many times you agree with RAGAS scores
5. **Update thesis**: Insert scores and agreement percentage in evaluation section

## Troubleshooting

### RAGAS Import Error

```
ERROR: RAGAS dependencies not installed. Please run:
  pip install ragas datasets
```

### No Questions Found

Ensure `data/faithfulness_questions.json` exists with at least 30 questions.

### API Rate Limits

The script includes retry logic with 21-second delays, matching the rest of the codebase.

### Low Scores

Check `ragas_evaluation_data.json` to see which questions failed and why.
