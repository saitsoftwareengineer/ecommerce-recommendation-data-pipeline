import pandas as pd
from sqlalchemy import create_engine, text

from rec_pipeline.data import generate_catalog, generate_events
from rec_pipeline.features import build_features, feature_columns
from rec_pipeline.pipeline import run


def test_events_and_catalog_generated():
    events, catalog = generate_events(n_users=50), generate_catalog()
    assert len(events) > 200 and len(catalog) == 120
    assert set(events["event_type"]) <= {"view", "cart", "purchase"}


def test_at_least_25_recommendation_features():
    features = build_features(generate_events(n_users=80), generate_catalog())
    cols = feature_columns(features)
    assert len(cols) >= 25, f"only {len(cols)} features: {cols}"
    assert features["label_purchased"].isin([0, 1]).all()


def test_features_stored_in_database(tmp_path):
    url = f"sqlite:///{tmp_path}/features.db"
    result = run(database_url=url)
    assert result["feature_rows"] > 0 and result["feature_count"] >= 25
    engine = create_engine(url)
    with engine.connect() as conn:
        n = conn.execute(text("SELECT COUNT(*) FROM recommendation_features")).scalar()
    assert n == result["feature_rows"]
