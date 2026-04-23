# Evaluation Files Structure

## **CLEAN FILE STRUCTURE (Use These Files)**

### 1. **Gold Standard Dataset (Semantic Mapping)**

- **Primary File**: `gold_standard_50_terms.json`
- **Description**: 50 German financial terms stratified into 7 categories
- **Used by**: `backend/evaluate.py` → `eval_semantic_mapping()`
- **Format**: JSON array with `german`, `english`, `category`, `difficulty`, `notes`

### 2. **Faithfulness Questions**

- **Primary File**: `faithfulness_questions.json`
- **Description**: 30 questions for faithfulness evaluation
- **Used by**: `backend/evaluate.py` → `eval_faithfulness()`
- **Format**: JSON array of question strings

### 3. **Comprehensive Faithfulness Dataset**

- **Reference File**: `faithfulness_questions_40.json`
- **Description**: 40 questions with metadata (id, category, difficulty, etc.)
- **Used for**: Reference and detailed analysis
- **Format**: JSON array with full question metadata

### 4. **Mapping Dictionary (System Component)**

- **File**: `mapping_dictionary.json`
- **Description**: Static dictionary for fast semantic mapping
- **Used by**: `backend/semantic.py` → `map_fields()`
- **Format**: JSON object {german_term: english_field}

### 5. **Sample Financial Data**

- **Files**: `JAB_*.json` (Maresi, Senna, Bitpanda, Smarter_Ecommerce)
- **Description**: Sample Austrian annual financial reports
- **Used for**: Testing and demonstration
- **Format**: JSON financial data in various structures

## **DEPRECATED FILES (Backed up in `backup/` folder)**

1. `ground_truth_mapping.json` - Old 6-term dataset
2. `ground_truth_mapping_50.json` - Duplicate of 50-term data

## **HOW EVALUATION WORKS**

### Semantic Mapping Evaluation:

```
evaluate.py → eval_semantic_mapping()
    ↓
Loads: gold_standard_50_terms.json
    ↓
Tests 50 terms against semantic mapper
    ↓
Calculates: Precision, Recall, F1 Score
    ↓
Checks: Precision ≥ 85%, Recall ≥ 80%
```

### Faithfulness Evaluation:

```
evaluate.py → eval_faithfulness()
    ↓
Loads: faithfulness_questions.json
    ↓
Runs 30 questions through RAG pipeline
    ↓
Checks: Answer faithfulness to sources
    ↓
Calculates: Faithfulness Score
    ↓
Checks: Score ≥ 85% (≥26/30 faithful)
```

## **RUNNING EVALUATIONS**

```bash
cd /Users/patrick/MA_MVP_Prototype_TEST/backend
python3 evaluate.py
```

## **FILE RELATIONSHIPS**

```
data/
├── gold_standard_50_terms.json        # ← eval_semantic_mapping() uses this
├── faithfulness_questions.json         # ← eval_faithfulness() uses this
├── faithfulness_questions_40.json      # ← Reference (detailed metadata)
├── mapping_dictionary.json            # ← semantic.py uses this
├── JAB_*.json                         # ← Sample financial data
└── backup/                            # ← Old files (deprecated)
```

## **UPDATING THE DATASETS**

### To add more terms to gold standard:

1. Edit `gold_standard_50_terms.json`
2. Maintain structure: `german`, `english`, `category`, `difficulty`, `notes`
3. Run validation: `python3 test_gold_standard.py`

### To add more faithfulness questions:

1. Edit `faithfulness_questions.json` (simple array for evaluation)
2. Edit `faithfulness_questions_40.json` (detailed metadata for reference)
3. Keep at least 30 questions for proper evaluation

## **ACADEMIC REQUIREMENTS**

From AGENTS.md:

- **Gold Standard**: 50 terms stratified into categories
- **Faithfulness**: At least 30 queries, ≥85% faithfulness (≥26/30)
- **Precision**: ≥85% for semantic mapping
- **Recall**: ≥80% for semantic mapping

All evaluation files meet these requirements.
