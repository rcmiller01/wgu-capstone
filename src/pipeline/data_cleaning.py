"""
Defensive cleaning utilities.

clean_dataframe:
- enforces optional schema (presence, dtype),
- trims object columns,
- optional row drops on NA,
- optional per-column fillna,
- returns cleaned df + a small report.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple
import pandas as pd

@dataclass(frozen=True)
class CleanReport:
    rows_in: int
    rows_out: int
    cols: int
    na_counts: Dict[str, int]
    notes: Tuple[str, ...]

def clean_dataframe(
    df: pd.DataFrame,
    expected_schema: Optional[Dict[str, str]] = None,
    drop_na_cols: Optional[Iterable[str]] = None,
    fillna: Optional[Dict[str, object]] = None,
) -> Tuple[pd.DataFrame, CleanReport]:
    notes = []
    df = df.copy()
    rows_in, _ = df.shape

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype("string").str.strip()

    if expected_schema:
        missing = [c for c in expected_schema if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        for c, dtype in expected_schema.items():
            try:
                df[c] = df[c].astype(dtype)
            except Exception as exc:
                raise TypeError(f"Cannot cast column '{c}' to {dtype}: {exc}") from exc

    if drop_na_cols:
        before = len(df)
        df = df.dropna(subset=list(drop_na_cols))
        dropped = before - len(df)
        if dropped:
            notes.append(f"Dropped {dropped} rows due to NA in {list(drop_na_cols)}.")

    if fillna:
        df = df.fillna(fillna)

    report = CleanReport(
        rows_in=rows_in,
        rows_out=len(df),
        cols=df.shape[1],
        na_counts=df.isna().sum().to_dict(),
        notes=tuple(notes),
    )
    return df, report
