"""
Smoke-run entrypoint.
Usage: python -m src.pipeline
Optionally set CAPSTONE_CSV to a CSV path to demo cleaning.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from .data_cleaning import clean_dataframe

CSV_PATH = os.getenv("CAPSTONE_CSV", "")


def main() -> int:
    if CSV_PATH and Path(CSV_PATH).exists():
        df = pd.read_csv(CSV_PATH)
        _, rep = clean_dataframe(df)
        print("Rows in/out:", rep.rows_in, rep.rows_out)
        return 0
    print("Pipeline skeleton OK — set CAPSTONE_CSV to demo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
