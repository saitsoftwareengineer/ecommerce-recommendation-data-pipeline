"""Synthetic e-commerce product / transaction event generation."""
from __future__ import annotations

import numpy as np
import pandas as pd

CATEGORIES = ["electronics", "books", "fashion", "home", "sports", "beauty"]


def generate_catalog(n_products: int = 120, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "product_id": [f"P{100 + i}" for i in range(n_products)],
        "category": rng.choice(CATEGORIES, n_products),
        "price": rng.uniform(8, 900, n_products).round(2),
        "brand_tier": rng.choice(["budget", "mid", "premium"], n_products, p=[0.4, 0.4, 0.2]),
        "avg_rating": rng.uniform(2.8, 5.0, n_products).round(2),
        "catalog_age_days": rng.integers(10, 900, n_products),
    })


def generate_events(n_users: int = 400, seed: int = 42) -> pd.DataFrame:
    """User-product events: views, cart adds and purchases with timestamps."""
    rng = np.random.default_rng(seed)
    catalog = generate_catalog(seed=seed)
    # Popularity is skewed: a few products get most traffic (Zipf-like)
    popularity = 1.0 / np.arange(1, len(catalog) + 1)
    popularity = popularity / popularity.sum()
    rows = []
    base = pd.Timestamp("2026-01-01")
    for u in range(n_users):
        user_id = f"U{1000 + u}"
        taste = rng.choice(CATEGORIES)  # each user leans to one category
        n_events = rng.integers(4, 26)
        for _ in range(n_events):
            product = catalog.sample(1, weights=popularity).iloc[0]
            in_taste = product["category"] == taste
            p_buy = 0.30 if in_taste else 0.10
            event = rng.choice(
                ["view", "cart", "purchase"],
                p=[1 - p_buy - 0.12, 0.12, p_buy],
            )
            rows.append({
                "user_id": user_id,
                "product_id": product["product_id"],
                "event_type": event,
                "quantity": int(rng.integers(1, 4)) if event == "purchase" else 0,
                "event_ts": base + pd.Timedelta(days=int(rng.integers(0, 120)),
                                                hours=int(rng.integers(0, 24))),
                "user_home_category": taste,
            })
    return pd.DataFrame(rows)
