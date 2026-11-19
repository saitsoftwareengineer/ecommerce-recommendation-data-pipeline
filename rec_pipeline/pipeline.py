"""End-to-end: generate events -> build features -> store in database."""
from __future__ import annotations

from rec_pipeline.data import generate_catalog, generate_events
from rec_pipeline.features import build_features, feature_columns
from rec_pipeline.store import store_features


def run(database_url: str | None = None) -> dict:
    catalog = generate_catalog()
    events = generate_events()
    features = build_features(events, catalog)
    rows = store_features(features, database_url)
    return {
        "events": int(len(events)),
        "feature_rows": int(rows),
        "feature_count": len(feature_columns(features)),
        "purchase_rate": round(float(features["label_purchased"].mean()), 4),
    }


if __name__ == "__main__":
    print(run())
