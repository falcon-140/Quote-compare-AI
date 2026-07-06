"""
compare.py

Loads the structured records produced by extract.py and builds a
side-by-side comparison table -- the actual deliverable an underwriter
or broker would look at.

Usage:
    python compare.py ../sample_output/extracted.json ../sample_output/comparison.csv
"""

import sys
import json
import pandas as pd

DISPLAY_COLUMNS = {
    "carrier_name": "Carrier",
    "annual_premium_usd": "Annual Premium ($)",
    "each_occurrence_limit_usd": "Per-Occurrence Limit ($)",
    "aggregate_limit_usd": "Aggregate Limit ($)",
    "deductible_usd": "Deductible ($)",
    "effective_date": "Effective",
    "expiration_date": "Expires",
    "key_exclusions": "Key Exclusions",
}


def build_comparison(input_path: str) -> pd.DataFrame:
    with open(input_path) as f:
        records = json.load(f)

    df = pd.DataFrame(records)

    # Flatten exclusions list into a readable string for the table.
    if "key_exclusions" in df.columns:
        df["key_exclusions"] = df["key_exclusions"].apply(
            lambda v: ", ".join(v) if isinstance(v, list) else v
        )

    df = df[[c for c in DISPLAY_COLUMNS if c in df.columns]]
    df = df.rename(columns=DISPLAY_COLUMNS)

    # Sort cheapest premium first -- the thing a buyer actually wants to see.
    if "Annual Premium ($)" in df.columns:
        df = df.sort_values("Annual Premium ($)")

    return df


def run(input_path: str, output_csv: str):
    df = build_comparison(input_path)
    df.to_csv(output_csv, index=False)

    print(df.to_markdown(index=False))
    print(f"\nSaved comparison table to {output_csv}")

    if "Annual Premium ($)" in df.columns and len(df) > 1:
        cheapest = df.iloc[0]
        priciest = df.iloc[-1]
        savings = priciest["Annual Premium ($)"] - cheapest["Annual Premium ($)"]
        print(
            f"\nCheapest option: {cheapest['Carrier']} "
            f"(${cheapest['Annual Premium ($)']:.2f}/yr, "
            f"${savings:.2f} less than the highest quote)"
        )


if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else "../sample_output/extracted.json"
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "../sample_output/comparison.csv"
    run(input_path, output_csv)
