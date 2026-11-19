# E-commerce Recommendation Data Pipeline

Builds recommendation features from product and transaction events:
synthetic event generation, joins and aggregations across users,
products and user×product pairs, and storage of the processed feature
table in a database for downstream recommendation models.

This is the project behind the resume line: *"Generated recommendation
features from product and transaction events by applying joins and
aggregations and storing processed features in PostgreSQL."*

## Tech stack
Python · Pandas (local path) · PySpark-style joins/aggregations ·
SQL · PostgreSQL (production) · SQLAlchemy · SQLite (local fallback)

> **PySpark / PostgreSQL notes:** every pandas `groupby`/`merge` here
> maps 1:1 to a Spark `groupBy().agg()` / join, so the same logic runs
> on a cluster with PySpark. Storage is PostgreSQL when `DATABASE_URL`
> points at one (see `sql/schema.sql`); otherwise it falls back to a
> local SQLite file so the pipeline and tests run anywhere.

## How to run
```bash
pip install -r requirements.txt
python run_pipeline.py     # prints event / row / feature counts
pytest                     # run the tests

# Against PostgreSQL:
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/shop \
  python run_pipeline.py
```

## Features built (25+ per user×product pair)
User: total events, views, carts, purchases, spend (total/mean),
unique products/categories, recency, active span, purchase/cart rates.
Product: total events, views, purchases, unique users, revenue,
conversion, price, rating, catalog age, category, brand tier.
Pair: events, views, carts, purchases, spend, recency, category match,
plus the `label_purchased` target.

## Project structure
```
rec_pipeline/data.py       synthetic catalog + product/transaction events
rec_pipeline/features.py   joins/aggregations -> 25+ recommendation features
rec_pipeline/store.py      SQLAlchemy storage (PostgreSQL / SQLite fallback)
rec_pipeline/pipeline.py   end-to-end run
sql/schema.sql             production PostgreSQL schema
run_pipeline.py            CLI entry point
tests/                     feature-count, generation and database tests
```
