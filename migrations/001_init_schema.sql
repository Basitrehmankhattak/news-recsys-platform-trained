BEGIN;

-- Step 3: Extensions
-- Why: We need reliable UUID generation for event IDs (impressions, clicks, sessions).
-- gen_random_uuid() comes from pgcrypto (recommended).
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
-- Step 4: Lookup tables (safer than Postgres ENUM in production)

CREATE TABLE IF NOT EXISTS model_component_types (
  component TEXT PRIMARY KEY
);

INSERT INTO model_component_types(component) VALUES
  ('retriever'),
  ('ranker'),
  ('reranker_policy'),
  ('faiss_index')
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS experiment_status_types (
  status TEXT PRIMARY KEY
);

INSERT INTO experiment_status_types(status) VALUES
  ('planned'),
  ('running'),
  ('stopped'),
  ('completed')
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS engagement_event_types (
  event_type TEXT PRIMARY KEY
);

INSERT INTO engagement_event_types(event_type) VALUES
  ('open'),
  ('save'),
  ('share'),
  ('hide'),
  ('dwell'),
  ('scroll')
ON CONFLICT DO NOTHING;

-- Step 5: users (minimal identity anchor)
CREATE TABLE IF NOT EXISTS users (
  user_id BIGSERIAL PRIMARY KEY,
  external_user_key TEXT UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Step 6: items (news catalog / item master)
CREATE TABLE IF NOT EXISTS items (
  item_id TEXT PRIMARY KEY,       -- MIND news_id, e.g. 'N12345'
  category TEXT,
  subcategory TEXT,
  title TEXT,
  abstract TEXT,
  entities JSONB,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Step 7: sessions (connects requests + events)
-- Why: supports anonymous usage, groups behavior, and anchors impressions.

CREATE TABLE IF NOT EXISTS sessions (
  session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
  anonymous_id TEXT,
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ended_at TIMESTAMPTZ,
  user_agent TEXT,
  device_type TEXT,
  app_version TEXT,
  referrer TEXT
);

-- Step 8: model_versions (lineage)
-- Why: every impression must be traceable to the exact retriever/ranker/index used.

CREATE TABLE IF NOT EXISTS model_versions (
  model_version_id BIGSERIAL PRIMARY KEY,
  component TEXT NOT NULL REFERENCES model_component_types(component),
  version_tag TEXT NOT NULL,           -- e.g., git sha or semantic version
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  training_data_snapshot TEXT,         -- optional: dataset hash/path
  metrics_summary JSONB,               -- optional: offline metrics summary
  config JSONB,                        -- optional: hyperparams/feature config
  UNIQUE(component, version_tag)
);
-- Step 9: experiments (A/B testing support)
-- Why: allows clean comparison of model variants without redesigning schema later.

CREATE TABLE IF NOT EXISTS experiments (
  experiment_id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  status TEXT NOT NULL REFERENCES experiment_status_types(status),
  start_at TIMESTAMPTZ,
  end_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS experiment_assignments (
  assignment_id BIGSERIAL PRIMARY KEY,
  experiment_id BIGINT NOT NULL REFERENCES experiments(experiment_id) ON DELETE CASCADE,
  user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
  anonymous_id TEXT,
  variant TEXT NOT NULL,   -- e.g. 'control', 'treatment_a'
  assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (user_id IS NOT NULL OR anonymous_id IS NOT NULL),
  UNIQUE (experiment_id, user_id),
  UNIQUE (experiment_id, anonymous_id)
);
-- Step 10: impressions_served (one row per recommendation response)
-- Why: logs exposure + model lineage so metrics/training are trustworthy.

CREATE TABLE IF NOT EXISTS impressions_served (
  impression_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,

  user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
  anonymous_id TEXT,
  served_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  surface TEXT,     -- e.g. 'home', 'sports', 'tech'
  page_size INT,
  locale TEXT,

  -- model lineage
  retriever_model_version_id BIGINT REFERENCES model_versions(model_version_id),
  faiss_index_version_id BIGINT REFERENCES model_versions(model_version_id),
  ranker_model_version_id BIGINT REFERENCES model_versions(model_version_id),
  reranker_policy_version_id BIGINT REFERENCES model_versions(model_version_id),

  -- experiment info (optional, but supported)
  experiment_id BIGINT REFERENCES experiments(experiment_id),
  experiment_variant TEXT,

  -- latency KPIs
  latency_ms_total INT,
  latency_ms_retrieval INT,
  latency_ms_ranking INT,
  latency_ms_rerank INT
);

-- Step 10b: impression_items (items shown inside one impression)
-- Why: stores ordering + scores for position bias, debugging, training extraction.

CREATE TABLE IF NOT EXISTS impression_items (
  impression_id UUID NOT NULL REFERENCES impressions_served(impression_id) ON DELETE CASCADE,
  position INT NOT NULL,
  item_id TEXT NOT NULL REFERENCES items(item_id) ON DELETE RESTRICT,

  retrieval_score DOUBLE PRECISION,
  rank_score DOUBLE PRECISION,
  final_score DOUBLE PRECISION,
  rerank_reason JSONB,
  is_exploration BOOLEAN NOT NULL DEFAULT FALSE,

  PRIMARY KEY (impression_id, position),
  UNIQUE (impression_id, item_id),
  CHECK (position >= 1)
);
-- Step 11: clicks (user interaction)
-- Why: links response to exposure (impression) so training + evaluation are correct.

CREATE TABLE IF NOT EXISTS clicks (
  click_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  impression_id UUID NOT NULL REFERENCES impressions_served(impression_id) ON DELETE CASCADE,
  item_id TEXT NOT NULL REFERENCES items(item_id) ON DELETE RESTRICT,
  position INT, -- denormalized for convenience (should match impression_items)
  clicked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  dwell_ms INT,
  open_type TEXT
);

-- Enforce idempotent click logging: one click per (impression_id, item_id)
ALTER TABLE clicks
ADD CONSTRAINT unique_click_per_item_per_impression
UNIQUE (impression_id, item_id);

-- Step 11b: indexes for core query paths

CREATE INDEX IF NOT EXISTS idx_impressions_served_at ON impressions_served(served_at);
CREATE INDEX IF NOT EXISTS idx_impressions_session ON impressions_served(session_id);
CREATE INDEX IF NOT EXISTS idx_impressions_user ON impressions_served(user_id, served_at);
CREATE INDEX IF NOT EXISTS idx_impressions_anon ON impressions_served(anonymous_id, served_at);

CREATE INDEX IF NOT EXISTS idx_imp_items_item ON impression_items(item_id);
CREATE INDEX IF NOT EXISTS idx_imp_items_impression ON impression_items(impression_id);

CREATE INDEX IF NOT EXISTS idx_clicks_clicked_at ON clicks(clicked_at);
CREATE INDEX IF NOT EXISTS idx_clicks_impression ON clicks(impression_id);
CREATE INDEX IF NOT EXISTS idx_clicks_item ON clicks(item_id, clicked_at);

-- Step 12: engagement_events (optional future-proof interactions)

CREATE TABLE IF NOT EXISTS engagement_events (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES sessions(session_id) ON DELETE CASCADE,
  impression_id UUID REFERENCES impressions_served(impression_id) ON DELETE CASCADE,
  item_id TEXT REFERENCES items(item_id) ON DELETE RESTRICT,

  event_type TEXT NOT NULL REFERENCES engagement_event_types(event_type),
  event_value JSONB,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMIT;
