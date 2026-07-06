"""
extract.py

Given a folder of insurance quote PDFs (any layout/carrier), this pulls the
raw text out of each PDF and asks Claude to return a normalized, structured
JSON record for it -- the same set of fields regardless of how each carrier
phrased or ordered them in the original document.

This is the core "quote comparison" building block: turn N differently
formatted documents into one consistent schema so they can be diffed,
ranked, or joined in a table.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python extract.py ../sample_quotes ../sample_output/extracted.json
"""

import os
import sys
import json
import glob

import pdfplumber
from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

SCHEMA_FIELDS = [
    "carrier_name",
    "quote_or_reference_number",
    "policy_type",
    "effective_date",
    "expiration_date",
    "annual_premium_usd",
    "each_occurrence_limit_usd",
    "aggregate_limit_usd",
    "deductible_usd",
    "key_exclusions",
    "payment_terms",
]

EXTRACTION_PROMPT = f"""You are extracting structured data from an insurance
quote document for a side-by-side comparison tool. Carriers phrase and order
the same underlying facts differently (e.g. "Deductible", "Retention",
"Per-Occurrence Cap" may all describe similar concepts) -- normalize them into
this exact JSON schema:

{json.dumps(SCHEMA_FIELDS, indent=2)}

Rules:
- Return ONLY a single JSON object, no markdown fences, no commentary.
- Money fields must be plain numbers (no "$", no commas), e.g. 4850.00.
- Dates must be formatted YYYY-MM-DD.
- "key_exclusions" must be a JSON array of short strings.
- If a field is genuinely not present in the document, use null.

Document text:
---
{{document_text}}
---
"""


def extract_pdf_text(pdf_path: str) -> str:
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)


def extract_structured_fields(client: Anthropic, document_text: str) -> dict:
    prompt = EXTRACTION_PROMPT.format(document_text=document_text)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    # Defensive cleanup in case the model wraps the JSON in fences anyway.
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:]
    return json.loads(raw)


def run(input_dir: str, output_path: str):
    client = Anthropic()  # reads ANTHROPIC_API_KEY from env
    pdf_paths = sorted(glob.glob(os.path.join(input_dir, "*.pdf")))

    if not pdf_paths:
        print(f"No PDFs found in {input_dir}")
        sys.exit(1)

    results = []
    for pdf_path in pdf_paths:
        print(f"Extracting: {os.path.basename(pdf_path)}")
        text = extract_pdf_text(pdf_path)
        try:
            fields = extract_structured_fields(client, text)
        except Exception as e:
            print(f"  Failed to extract {pdf_path}: {e}")
            continue
        fields["_source_file"] = os.path.basename(pdf_path)
        results.append(fields)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nWrote {len(results)} extracted records to {output_path}")


if __name__ == "__main__":
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "../sample_quotes"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "../sample_output/extracted.json"
    run(input_dir, output_path)
