"""Recommendation feature engineering.

PySpark-style joins and aggregations (groupBy / join / window-style
rolling stats), implemented in pandas so the pipeline runs locally and
in tests. On a cluster, each groupby maps 1:1 to a Spark
`groupBy().agg()` and each merge to a Spark join -- see README.

Builds one row per (user, product) pair the user interacted with, with
25+ features describing the user, the product, and the pair.
"""
from __future__ import annotations

import pandas as pd

REFERENCE_DATE = pd.Timestamp("2026-04-30")


def build_features(events: pd.DataFrame, catalog: pd.DataFrame) -> pd.DataFrame:
    ev = events.copy()
    ev["is_view"] = (ev["event_type"] == "view").astype(int)
    ev["is_cart"] = (ev["event_type"] == "cart").astype(int)
    ev["is_purchase"] = (ev["event_type"] == "purchase").astype(int)
    ev = ev.merge(catalog, on="product_id", how="left")
    ev["spend"] = ev["quantity"] * ev["price"]
    ev["category_match"] = (ev["category"] == ev["user_home_category"]).astype(int)

    # --- user-level aggregates ---
    user = ev.groupby("user_id").agg(
        user_total_events=("event_type", "size"),
        user_views=("is_view", "sum"),
        user_carts=("is_cart", "sum"),
        user_purchases=("is_purchase", "sum"),
        user_total_spend=("spend", "sum"),
        user_avg_spend=("spend", "mean"),
        user_unique_products=("product_id", "nunique"),
        user_unique_categories=("category", "nunique"),
        user_last_event=("event_ts", "max"),
        user_first_event=("event_ts", "min"),
    ).reset_index()
    user["user_recency_days"] = (REFERENCE_DATE - user["user_last_event"]).dt.days
    user["user_active_span_days"] = (
        (user["user_last_event"] - user["user_first_event"]).dt.days + 1
    )
    user["user_purchase_rate"] = user["user_purchases"] / user["user_total_events"]
    user["user_cart_rate"] = user["user_carts"] / user["user_total_events"]
    user = user.drop(columns=["user_last_event", "user_first_event"])

    # --- product-level aggregates ---
    prod = ev.groupby("product_id").agg(
        product_total_events=("event_type", "size"),
        product_views=("is_view", "sum"),
        product_purchases=("is_purchase", "sum"),
        product_unique_users=("user_id", "nunique"),
        product_revenue=("spend", "sum"),
    ).reset_index()
    prod["product_conversion"] = prod["product_purchases"] / prod["product_total_events"]

    # --- user x product pair aggregates ---
    pair = ev.groupby(["user_id", "product_id"]).agg(
        pair_events=("event_type", "size"),
        pair_views=("is_view", "sum"),
        pair_carts=("is_cart", "sum"),
        pair_purchases=("is_purchase", "sum"),
        pair_spend=("spend", "sum"),
        pair_last_event=("event_ts", "max"),
        pair_category_match=("category_match", "max"),
    ).reset_index()
    pair["pair_recency_days"] = (REFERENCE_DATE - pair["pair_last_event"]).dt.days
    pair = pair.drop(columns=["pair_last_event"])
    pair["label_purchased"] = (pair["pair_purchases"] > 0).astype(int)

    out = (
        pair.merge(user, on="user_id", how="left")
        .merge(prod, on="product_id", how="left")
        .merge(catalog, on="product_id", how="left")
    )
    out = out.rename(columns={
        "price": "product_price", "avg_rating": "product_avg_rating",
        "catalog_age_days": "product_catalog_age_days",
    })
    return out


def feature_columns(df: pd.DataFrame) -> list[str]:
    excluded = {"user_id", "product_id", "category", "brand_tier",
                "user_home_category", "label_purchased"}
    return [c for c in df.columns if c not in excluded]
