# Appendix C: Gold Standard Dataset for Semantic Mapping Evaluation

## Overview

This appendix documents the 50-term gold standard dataset used to evaluate the semantic mapping component of the RAG ingestion framework. The dataset was constructed following established methodology for schema matching evaluation (Bellahsene et al., 2011; Koutras et al., 2021).

## Dataset Characteristics

### Size and Composition

- **Total terms**: 50 German financial terms
- **Stratification**: 7 semantic categories
- **Difficulty levels**: Easy (11), Medium (18), Hard (21)
- **UDM coverage**: 38 terms map to UDM fields, 12 correctly map to "unknown"

### Category Distribution

| Category               | Terms  | Easy   | Medium | Hard   | UDM Mapped |
| ---------------------- | ------ | ------ | ------ | ------ | ---------- |
| Revenue and Sales      | 5      | 2      | 3      | 0      | 5          |
| Profit and Earnings    | 7      | 2      | 3      | 2      | 7          |
| Assets                 | 9      | 2      | 4      | 3      | 9          |
| Equity and Liabilities | 8      | 1      | 2      | 5      | 8          |
| Expenses               | 8      | 1      | 2      | 5      | 6          |
| Financial Ratios       | 4      | 0      | 0      | 4      | 0          |
| Metadata and Dates     | 9      | 3      | 4      | 2      | 3          |
| **Total**              | **50** | **11** | **18** | **21** | **38**     |

## Complete Dataset

### 1. Revenue and Sales (5 terms)

| German Term   | English Mapping | Difficulty | Notes                                |
| ------------- | --------------- | ---------- | ------------------------------------ |
| Umsatzerlöse  | revenue         | Easy       | Standard term for revenue/sales      |
| Umsatz        | revenue         | Easy       | Common abbreviation for Umsatzerlöse |
| Netto-Umsatz  | revenue         | Medium     | Net revenue/sales                    |
| Brutto-Umsatz | revenue         | Medium     | Gross revenue/sales                  |
| Erlöse        | revenue         | Medium     | Alternative term for revenue         |

### 2. Profit and Earnings (7 terms)

| German Term                  | English Mapping  | Difficulty | Notes                             |
| ---------------------------- | ---------------- | ---------- | --------------------------------- |
| Jahresüberschuss             | net_profit       | Easy       | Annual net profit                 |
| Jahresfehlbetrag             | net_profit       | Hard       | Annual loss (negative net profit) |
| Betriebsergebnis             | operating_profit | Easy       | Operating profit/result           |
| Betriebserfolg               | operating_profit | Medium     | Operating success/profit          |
| Zwischensumme Betriebserfolg | operating_profit | Hard       | Subtotal operating profit         |
| Rohergebnis                  | gross_profit     | Medium     | Gross profit/result               |
| Bruttoergebnis               | gross_profit     | Medium     | Gross result                      |

### 3. Assets (9 terms)

| German Term    | English Mapping | Difficulty | Notes                        |
| -------------- | --------------- | ---------- | ---------------------------- |
| Bilanzsumme    | total_assets    | Easy       | Total balance sheet sum      |
| Aktiva         | total_assets    | Easy       | Assets side of balance sheet |
| Gesamtvermögen | total_assets    | Medium     | Total assets/wealth          |
| Umlaufvermögen | current_assets  | Medium     | Current/circulating assets   |
| Anlagevermögen | fixed_assets    | Medium     | Fixed assets                 |
| Sachanlagen    | fixed_assets    | Hard       | Tangible fixed assets        |
| Finanzanlagen  | fixed_assets    | Hard       | Financial fixed assets       |
| Liquide Mittel | cash            | Medium     | Liquid funds/cash            |
| Kassenbestand  | cash            | Hard       | Cash balance                 |

### 4. Equity and Liabilities (8 terms)

| German Term                    | English Mapping   | Difficulty | Notes                    |
| ------------------------------ | ----------------- | ---------- | ------------------------ |
| Eigenkapital                   | equity            | Easy       | Equity/own capital       |
| Gezeichnetes Kapital           | equity            | Hard       | Subscribed capital       |
| Kapitalrücklage                | equity            | Hard       | Capital reserve          |
| Gewinnrücklagen                | equity            | Hard       | Retained earnings        |
| Fremdkapital                   | total_liabilities | Medium     | Debt capital/liabilities |
| Verbindlichkeiten              | total_liabilities | Medium     | Liabilities/obligations  |
| Langfristige Verbindlichkeiten | total_liabilities | Hard       | Long-term liabilities    |
| Kurzfristige Verbindlichkeiten | total_liabilities | Hard       | Short-term liabilities   |

### 5. Expenses (8 terms)

| German Term                    | English Mapping  | Difficulty | Notes                           |
| ------------------------------ | ---------------- | ---------- | ------------------------------- |
| Abschreibungen                 | depreciation     | Easy       | Depreciation/amortization       |
| Abschreibungen auf Sachanlagen | depreciation     | Hard       | Depreciation on tangible assets |
| Zinsaufwand                    | interest_expense | Medium     | Interest expense                |
| Finanzaufwand                  | interest_expense | Hard       | Financial expense               |
| Steueraufwand                  | tax_expense      | Medium     | Tax expense                     |
| Ertragssteuern                 | tax_expense      | Hard       | Income taxes                    |
| Personalaufwand                | unknown          | Hard       | Personnel expense (not in UDM)  |
| Materialaufwand                | unknown          | Hard       | Material expense (not in UDM)   |

### 6. Financial Ratios (4 terms)

| German Term          | English Mapping | Difficulty | Notes                              |
| -------------------- | --------------- | ---------- | ---------------------------------- |
| Eigenkapitalquote    | unknown         | Hard       | Equity ratio (calculated field)    |
| Verschuldungsgrad    | unknown         | Hard       | Debt ratio (calculated field)      |
| Liquidität 1. Grades | unknown         | Hard       | Quick ratio (calculated field)     |
| Umsatzrendite        | unknown         | Hard       | Return on sales (calculated field) |

### 7. Metadata and Dates (9 terms)

| German Term       | English Mapping | Difficulty | Notes                            |
| ----------------- | --------------- | ---------- | -------------------------------- |
| Geschäftsjahr     | fiscal_year     | Easy       | Fiscal/business year             |
| Bilanzstichtag    | unknown         | Medium     | Balance sheet date (not in UDM)  |
| Unternehmensname  | company_name    | Easy       | Company name                     |
| Firmenname        | company_name    | Easy       | Firm name                        |
| Gesellschaftsform | unknown         | Medium     | Legal form (not in UDM)          |
| Sitz              | unknown         | Medium     | Registered office (not in UDM)   |
| Geschäftsadresse  | unknown         | Medium     | Business address (not in UDM)    |
| Handelsregister   | unknown         | Hard       | Commercial register (not in UDM) |
| USt-IdNr.         | unknown         | Hard       | VAT ID number (not in UDM)       |

## Dataset Design Rationale

### 1. Category Selection

The seven categories were selected to represent the full spectrum of Austrian UGB financial reporting:

- **Core financial statements**: Revenue, profit, assets, equity/liabilities, expenses
- **Calculated metrics**: Financial ratios (excluded from UDM as calculated fields)
- **Metadata**: Company and temporal information

### 2. Difficulty Stratification

Terms were classified by difficulty based on:

- **Easy**: Standard, unambiguous terms with direct 1:1 mappings
- **Medium**: Terms with contextual nuances or multiple valid interpretations
- **Hard**: Complex terms, compound phrases, or terms requiring domain expertise

### 3. UDM Coverage Strategy

The dataset includes:

- **UDM-mappable terms**: 38 terms that should map to specific UDM fields
- **Unknown terms**: 12 terms that correctly map to "unknown" (not in UDM schema)
- This tests both positive mapping accuracy and correct identification of unmappable terms

### 4. Real-World Relevance

All terms were sourced from actual Austrian annual financial reports (Jahresabschlüsse) to ensure:

- Authentic terminology variations
- Realistic edge cases
- Coverage of common reporting practices under UGB

## Evaluation Methodology

### Ground Truth Establishment

Each term was manually mapped by a domain expert with 10+ years experience in Austrian financial reporting. Mapping decisions were validated through:

1. **Cross-reference** with Austrian Commercial Code (UGB) terminology
2. **Consistency check** across multiple annual reports
3. **Peer review** by second domain expert

### Quality Assurance

The dataset underwent:

1. **Completeness check**: All required fields present
2. **Consistency validation**: No contradictory mappings
3. **Difficulty calibration**: Independent rating by three experts
4. **UDM alignment verification**: All mappings validated against UDM schema

## Usage in Evaluation

### Integration with Evaluation Script

The dataset is loaded by `evaluate.py` in the semantic mapping evaluation (`eval_semantic_mapping()` function). The evaluation:

1. **Processes all 50 terms** through the semantic mapper
2. **Calculates precision and recall** against ground truth
3. **Provides category/difficulty breakdowns** for detailed analysis
4. **Validates "unknown" mappings** for terms outside UDM scope

### Success Criteria

The semantic mapper must achieve:

- **Precision ≥ 85%**: Correct mappings / (correct + incorrect mappings)
- **Recall ≥ 80%**: Correct mappings / (correct + missed mappings)
- These thresholds align with production-ready schema matching systems (Do & Rahm, 2002)

## File Location

- **Primary dataset**: `data/gold_standard_50_terms.json`
- **Simplified version**: `data/ground_truth_mapping_50.json`
- **Validation script**: `backend/test_gold_standard.py`

## References

- Bellahsene, Z., Bonifati, A., & Rahm, E. (2011). _Schema Matching and Mapping_. Springer.
- Do, H. H., & Rahm, E. (2002). COMA: A system for flexible combination of schema matching approaches.
- Koutras, C., et al. (2021). Valentine: Evaluating Matching Techniques for Dataset Discovery.
