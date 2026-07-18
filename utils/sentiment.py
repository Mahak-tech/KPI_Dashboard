"""
sentiment.py
------------
Helper functions to run sentiment analysis on text using TextBlob
and to derive KPI-ready fields from a reviews DataFrame.
"""

import pandas as pd
from textblob import TextBlob


def get_polarity(text: str) -> float:
    """Return polarity score in range [-1.0, 1.0]."""
    if not isinstance(text, str) or not text.strip():
        return 0.0
    return TextBlob(text).sentiment.polarity


def get_subjectivity(text: str) -> float:
    """Return subjectivity score in range [0.0, 1.0]."""
    if not isinstance(text, str) or not text.strip():
        return 0.0
    return TextBlob(text).sentiment.subjectivity


def classify_sentiment(polarity: float, pos_thresh: float = 0.05, neg_thresh: float = -0.05) -> str:
    """Classify a polarity score into Positive / Neutral / Negative."""
    if polarity > pos_thresh:
        return "Positive"
    elif polarity < neg_thresh:
        return "Negative"
    return "Neutral"


def enrich_dataframe(df: pd.DataFrame, text_col: str = "review") -> pd.DataFrame:
    """
    Add polarity, subjectivity, sentiment label, and word_count columns
    to the given DataFrame based on the text_col column.
    """
    df = df.copy()
    df["polarity"] = df[text_col].apply(get_polarity)
    df["subjectivity"] = df[text_col].apply(get_subjectivity)
    df["sentiment"] = df["polarity"].apply(classify_sentiment)
    df["word_count"] = df[text_col].astype(str).apply(lambda t: len(t.split()))
    return df


def compute_kpis(df: pd.DataFrame) -> dict:
    """Compute headline KPI values from an enriched DataFrame."""
    total = len(df)
    if total == 0:
        return {
            "total_reviews": 0,
            "avg_polarity": 0.0,
            "avg_rating": 0.0,
            "pct_positive": 0.0,
            "pct_neutral": 0.0,
            "pct_negative": 0.0,
        }

    counts = df["sentiment"].value_counts()
    return {
        "total_reviews": total,
        "avg_polarity": round(df["polarity"].mean(), 3),
        "avg_rating": round(df["rating"].mean(), 2) if "rating" in df.columns else None,
        "pct_positive": round(100 * counts.get("Positive", 0) / total, 1),
        "pct_neutral": round(100 * counts.get("Neutral", 0) / total, 1),
        "pct_negative": round(100 * counts.get("Negative", 0) / total, 1),
    }
