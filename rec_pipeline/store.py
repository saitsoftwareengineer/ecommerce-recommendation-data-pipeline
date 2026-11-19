"""Store processed features in a database table.

PostgreSQL in production (set DATABASE_URL, e.g.
postgresql+psycopg2://user:pass@host/db); SQLite is the local/test
fallback so the pipeline runs anywhere.
"""
from __future__ import annotations

import os

import pandas as pd
from sqlalchemy import create_engine, inspect

TABLE = "recommendation_features"


def get_engine(database_url: str | None = None):
    url = database_url or os.environ.get("DATABASE_URL", "sqlite:///features.db")
    return create_engine(url)


def store_features(df: pd.DataFrame, database_url: str | None = None) -> int:
    engine = get_engine(database_url)
    df.to_sql(TABLE, engine, if_exists="replace", index=False)
    assert TABLE in inspect(engine).get_table_names()
    return len(df)
