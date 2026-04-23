from typing import TypedDict, Optional, Dict, Any

class UnifiedDocumentModel(TypedDict):
    """
    Standardized schema for all extracted financial information regardless
    of whether the source was a structured JSON or unstructured PDF.
    """
    company_name: str
    fiscal_year: int
    source_format: str
    source_file: str
    
    # Income statement fields
    revenue: Optional[float]
    gross_profit: Optional[float]
    operating_profit: Optional[float]
    net_profit: Optional[float]
    interest_expense: Optional[float]
    tax_expense: Optional[float]
    depreciation: Optional[float]

    # Balance sheet fields
    total_assets: Optional[float]
    current_assets: Optional[float]
    fixed_assets: Optional[float]
    total_liabilities: Optional[float]
    equity: Optional[float]
    cash: Optional[float]
    
    # Raw content fallbacks
    raw_text: Optional[str]
    metadata: Dict[str, Any]
