"""Shared product-name matching so /compare and /predict agree."""
import pandas as pd


def find_listings(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """Exact (case-insensitive) product-name match first; if there is none,
    fall back to a literal substring match."""
    lowered = df["product_name"].str.lower()
    q = name.strip().lower()
    exact = df[lowered == q]
    if not exact.empty:
        return exact
    return df[lowered.str.contains(q, na=False, regex=False)]


def resolve_product_name(df: pd.DataFrame, name: str):
    """Return the single canonical product_name for `name`, or None.
    For a partial query, picks the product with the most listings."""
    matches = find_listings(df, name)
    if matches.empty:
        return None
    return matches["product_name"].value_counts().idxmax()
