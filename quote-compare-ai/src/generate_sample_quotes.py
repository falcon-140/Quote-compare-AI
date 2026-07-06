"""
generate_sample_quotes.py

Creates a handful of realistic-looking (but entirely synthetic) commercial
insurance quote PDFs so the extraction pipeline can be demoed end-to-end
without needing real, sensitive client documents.

Each PDF intentionally uses a different layout / wording, the way real quotes
from different carriers would, so the extraction step has to actually read
and normalize the content rather than pattern-match one template.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "sample_quotes")
os.makedirs(OUT_DIR, exist_ok=True)


def draw_quote(filename, lines, title="INSURANCE QUOTE PROPOSAL"):
    path = os.path.join(OUT_DIR, filename)
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, height - 1 * inch, title)
    c.setFont("Helvetica", 10)

    y = height - 1.4 * inch
    for line in lines:
        if line == "":
            y -= 0.15 * inch
            continue
        if line.startswith("## "):
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1 * inch, y, line[3:])
            c.setFont("Helvetica", 10)
        else:
            c.drawString(1 * inch, y, line)
        y -= 0.22 * inch

    c.save()
    print(f"Wrote {path}")


def build_all():
    # Carrier A — clean, direct layout
    draw_quote(
        "quote_summit_mutual.pdf",
        [
            "Carrier: Summit Mutual Insurance Group",
            "Quote Number: SM-2026-88214",
            "Effective Date: 08/01/2026    Expiration Date: 08/01/2027",
            "",
            "## Named Insured",
            "Vaishnavi Textiles LLC",
            "",
            "## Coverage Summary",
            "Policy Type: Commercial General Liability",
            "Annual Premium: $4,850.00",
            "General Aggregate Limit: $2,000,000",
            "Each Occurrence Limit: $1,000,000",
            "Deductible: $1,000 per claim",
            "",
            "## Additional Terms",
            "Excludes: Cyber liability, flood damage, employment practices",
            "Payment Terms: Annual, or quarterly with 3% surcharge",
        ],
    )

    # Carrier B — different terminology & ordering, includes a bundled line
    draw_quote(
        "quote_pacific_crest.pdf",
        [
            "PACIFIC CREST UNDERWRITERS",
            "Proposal Ref #: PCU-77341-A",
            "",
            "## Prepared For",
            "Vaishnavi Textiles LLC",
            "Policy Period: 09/15/2026 to 09/15/2027",
            "",
            "## Premium & Limits",
            "Total Annual Cost: $5,275.50",
            "Liability Limit (Occurrence): $1,000,000",
            "Aggregate Limit: $2,000,000",
            "Retention/Deductible: $2,500",
            "",
            "## Exclusions & Notes",
            "This quote does not include coverage for cyber incidents,",
            "flood, or professional errors & omissions.",
            "A 2% early-payment discount applies if paid in full within 10 days.",
        ],
    )

    # Carrier C — sparse layout, some fields phrased unusually
    draw_quote(
        "quote_harbor_point.pdf",
        [
            "Harbor Point Specialty Insurance",
            "Ref: HP-QT-556209",
            "",
            "Insured Business: Vaishnavi Textiles LLC",
            "Coverage Window: 07/01/2026 - 06/30/2027",
            "",
            "Yearly Rate: $4,390",
            "Per-Occurrence Cap: $1,000,000 USD",
            "Aggregate Cap (all claims): $2,000,000 USD",
            "Deductible Amount: $500",
            "",
            "Notes: Cyber events and flood-related losses are not covered",
            "under this proposal. Monthly installment plan available (+4% fee).",
        ],
    )


if __name__ == "__main__":
    build_all()
