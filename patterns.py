import re
from dataclasses import dataclass
from typing import List, Dict, Callable, Optional, Any

# Currency Mapping
CURRENCY_MAP = {
    '$': 'USD', '€': 'EUR', '£': 'GBP', '₹': 'INR', '¥': 'JPY', 'RM': 'MYR', 'S$': 'SGD',
    'USD': 'USD', 'EUR': 'EUR', 'GBP': 'GBP', 'INR': 'INR', 'JPY': 'JPY', 'MYR': 'MYR', 'SGD': 'SGD'
}

@dataclass
class FieldPattern:
    name: str
    keywords: List[str]
    regex: re.Pattern
    parser: Callable[[re.Match], Any]

# Configuration
pattern_config = {
    "amount": {
        "keywords": [
            "total", "amount", "grand total", "balance", "net amount", "subtotal",
            "final amount", "payment due", "amt due", "total payable", "current due",
            "outstanding balance", "sum", "including Tax", "TOTAL"
        ],
        "currency_symbols": list(CURRENCY_MAP.keys()) + list(CURRENCY_MAP.values()),
        "decimal_separators": [",", "."],
        "thousand_separators": [",", ".", " "]
    },
    "date": {
        "formats": [
            r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b",
            r"\b\d{1,2}\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{2,4}\b",
            r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b"
        ],
        "month_names": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    },
    "shop": {
        "suffixes": [
            "PETROLEUM", "GAS", "STORE", "SUPPLY", "SHOP", "MART", "FUEL",
            "SUPERMARKET", "DEALER", "TRADERS", "SERVICE", "CENTER", "OUTLET",
            "WHOLESALE", "DISTRIBUTORS", "AGENCY"
        ]
    },
    "items": {
        "units": ["LTR", "L", "LITERS", "ML", "KG", "KGS", "G", "GRAMS", "MG", "TON", "PCS"]
    },
    "tax": {
        "identifiers": ["GST", "VAT", "SVC CHG", "SERVICE CHARGE", "TAX", "SALES TAX"]
    },
    "invoice": {
        "prefixes": ["Invoice", "Bill", "Receipt", "Order", "Credit Note", "Debit Note", "Reference", "Tax Invoice", "Bill No"]
    },
    "payment": {
        "methods": ["Credit Card", "Debit Card", "Cash", "Cheque", "Online Transfer", "UPI", "Netbanking", "PayPal"]
    }
}

# Regex Generators
def create_amount_regex() -> re.Pattern:
    keywords = "|".join(pattern_config["amount"]["keywords"])
    currencies = "|".join(pattern_config["amount"]["currency_symbols"])
    regex = rf"\b(?:{keywords})[\s:]*" \
            rf"(?:({currencies})\s*)?" \
            rf"([\d{''.join(pattern_config['amount']['thousand_separators'])}]+(?:[{''.join(pattern_config['amount']['decimal_separators'])}]\d+)?)" \
            rf"(?:\s*({currencies}))?"
    return re.compile(regex, re.IGNORECASE)

def create_date_regex() -> re.Pattern:
    formats = "|".join(pattern_config["date"]["formats"])
    return re.compile(formats, re.IGNORECASE)

def create_shop_name_regex() -> re.Pattern:
    suffixes = "|".join(pattern_config["shop"]["suffixes"])
    return re.compile(rf"^(.*?)(?:\s*[,-]?\s*(?:{suffixes}))", re.IGNORECASE)

def create_invoice_regex() -> re.Pattern:
    prefixes = "|".join(pattern_config["invoice"]["prefixes"])
    return re.compile(rf"(?:{prefixes})[\s#:-]*([A-Z0-9-]{{3,}})", re.IGNORECASE)

def create_payment_regex() -> re.Pattern:
    methods = "|".join(pattern_config["payment"]["methods"])
    return re.compile(rf"(?:Payment|Paid\s*By)[\s:-]*({methods})", re.IGNORECASE)

# Parsers
def amount_parser(match: re.Match) -> Dict[str, Optional[str]]:
    currency = next((c for c in [match[1], match[3]] if c and c in CURRENCY_MAP), None)
    amount_str = re.sub(r"[^\d,.]", "", match[2])

    decimal_separator = next((sep for sep in pattern_config["amount"]["decimal_separators"] if sep in amount_str), None)
    if decimal_separator:
        amount_str = amount_str.replace(",", ".")
    
    return {"currency": CURRENCY_MAP.get(currency, None), "amount": float(amount_str)}

def shop_name_parser(match: re.Match) -> str:
    return match[1].strip()

def tax_parser(match: re.Match) -> str:
    return f"{match[1]}: {match[2]}"

def item_parser(match: re.Match) -> Dict[str, Any]:
    return {"quantity": match[1], "unit": match[2], "description": match[3], "price": match[4]}

def invoice_parser(match: re.Match) -> str:
    return match[1]

def payment_parser(match: re.Match) -> str:
    return match[1]

# Pattern List
PATTERNS: List[FieldPattern] = [
    FieldPattern(name="amount", keywords=pattern_config["amount"]["keywords"], regex=create_amount_regex(), parser=amount_parser),
    FieldPattern(name="date", keywords=pattern_config["date"]["formats"], regex=create_date_regex(), parser=lambda m: m.group()),
    FieldPattern(name="shopName", keywords=pattern_config["shop"]["suffixes"], regex=create_shop_name_regex(), parser=shop_name_parser),
    FieldPattern(name="items", keywords=pattern_config["items"]["units"], regex=re.compile(r"(\d+)\s*(" + "|".join(pattern_config["items"]["units"]) + r")\s+(.*?)\s+([\d.,]+)", re.IGNORECASE), parser=item_parser),
    FieldPattern(name="tax", keywords=pattern_config["tax"]["identifiers"], regex=re.compile(r"(" + "|".join(pattern_config["tax"]["identifiers"]) + r")[\s:@]*([\d.,]+)", re.IGNORECASE), parser=tax_parser),
    FieldPattern(name="invoiceNumber", keywords=pattern_config["invoice"]["prefixes"], regex=create_invoice_regex(), parser=invoice_parser),
    FieldPattern(name="paymentMethod", keywords=pattern_config["payment"]["methods"], regex=create_payment_regex(), parser=payment_parser)
]

