import pandas as pd
import numpy as np

_scored_cache = None


def _score_row(row, min_price: float, max_price: float) -> float:
    """
    AI Score (0-100) — weighted combination:

      - Price competitiveness  (40%) — cheaper than other listings of the same
                                       product = higher score
      - Rating score           (30%) — numeric rating 1-5
      - Review sentiment       (20%) — mapped to 1-5 scale
      - Recency score          (10%) — how fresh the listing is

    Price is the largest single factor, so the cheapest listing usually (but
    not always) has the highest AI score; rating and reviews can outweigh a
    small price gap.
    """

    # -- Price competitiveness (40%) --
    if pd.notna(min_price) and pd.notna(max_price) and max_price > min_price:
        price_score = ((max_price - row["price"]) / (max_price - min_price)) * 40
    else:
        price_score = 20.0  # single listing / all same price -> neutral

    # -- Rating score (30%) --
    rating = row.get("ratings_num")
    if pd.notna(rating) and rating > 0:
        rating_score = (min(float(rating), 5.0) / 5.0) * 30
    else:
        rating_score = 15.0

    # -- Review sentiment score (20%) --
    sentiment = row.get("review_sentiment")
    if pd.notna(sentiment):
        sentiment_score = (min(float(sentiment), 5.0) / 5.0) * 20
    else:
        review = str(row.get("reviews", "")).lower()
        if "excellent" in review:
            sentiment_score = 20.0
        elif "very good" in review:
            sentiment_score = 16.0
        elif "good" in review:
            sentiment_score = 13.0
        elif "average" in review or "decent" in review:
            sentiment_score = 10.0
        elif "not satisfactory" in review or "poor" in review:
            sentiment_score = 4.0
        else:
            sentiment_score = 10.0

    # -- Recency score (10%) --
    try:
        date = pd.to_datetime(row["date"])
        if pd.isna(date):
            raise ValueError("no date")
        days_old = max(0, (pd.Timestamp.now() - date).days)
        recency_score = max(0.0, (1 - days_old / 365)) * 10
    except Exception:
        recency_score = 5.0

    total = price_score + rating_score + sentiment_score + recency_score
    return round(min(max(total, 0.0), 100.0), 1)


def score_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Score every row. Price competitiveness is computed against all rows in
    `df` that share the same product_name (vectorised, O(n))."""
    df = df.copy()
    grp = df.groupby("product_name")["price"]
    mins = grp.transform("min")
    maxs = grp.transform("max")
    df["ai_score"] = [
        _score_row(row, mn, mx)
        for (_, row), mn, mx in zip(df.iterrows(), mins, maxs)
    ]
    return df


def get_scored_dataframe() -> pd.DataFrame:
    """Scored full dataset (cached). Always score the FULL dataset and filter
    afterwards, so a product's AI score is identical on the search page,
    comparison modal and product page regardless of filters applied."""
    global _scored_cache
    if _scored_cache is None:
        from utils.data_loader import get_dataframe
        _scored_cache = score_dataframe(get_dataframe())
    return _scored_cache.copy()
