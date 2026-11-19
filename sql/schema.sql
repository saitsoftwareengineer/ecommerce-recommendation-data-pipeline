-- PostgreSQL schema for the processed recommendation features table.
-- The pipeline creates/replaces this table via SQLAlchemy; this file
-- documents the production shape.
CREATE TABLE IF NOT EXISTS recommendation_features (
    user_id                 TEXT,
    product_id              TEXT,
    pair_events             BIGINT,
    pair_views              BIGINT,
    pair_carts              BIGINT,
    pair_purchases          BIGINT,
    pair_spend              DOUBLE PRECISION,
    pair_recency_days       BIGINT,
    pair_category_match     BIGINT,
    label_purchased         BIGINT,
    user_total_events       BIGINT,
    user_total_spend        DOUBLE PRECISION,
    user_purchase_rate      DOUBLE PRECISION,
    product_total_events    BIGINT,
    product_purchases       BIGINT,
    product_conversion      DOUBLE PRECISION,
    product_price           DOUBLE PRECISION,
    product_avg_rating      DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS idx_rec_feat_user ON recommendation_features (user_id);
CREATE INDEX IF NOT EXISTS idx_rec_feat_product ON recommendation_features (product_id);
