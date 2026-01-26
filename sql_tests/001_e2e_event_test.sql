\echo '--- Ensure test items exist ---'
INSERT INTO items(item_id, category, subcategory, title)
VALUES
  ('N_TEST_1', 'News', 'General', 'Test Article 1'),
  ('N_TEST_2', 'News', 'General', 'Test Article 2'),
  ('N_TEST_3', 'News', 'General', 'Test Article 3')
ON CONFLICT (item_id) DO NOTHING;

\echo '--- Create session and capture session_id ---'
INSERT INTO sessions(anonymous_id, device_type, app_version)
VALUES ('anon_123', 'desktop', 'streamlit_dev')
RETURNING session_id \gset

\echo 'Session ID is : :session_id'

\echo '--- Create impression and capture impression_id ---'
INSERT INTO impressions_served(session_id, anonymous_id, surface, page_size, locale)
VALUES (:'session_id', 'anon_123', 'home', 3, 'en-US')
RETURNING impression_id \gset

\echo 'Impression ID is : :impression_id'

\echo '--- Insert shown items for that impression ---'
INSERT INTO impression_items(impression_id, position, item_id, retrieval_score, rank_score, final_score)
VALUES
  (:'impression_id', 1, 'N_TEST_2', 0.81, 0.72, 0.70),
  (:'impression_id', 2, 'N_TEST_1', 0.77, 0.60, 0.58),
  (:'impression_id', 3, 'N_TEST_3', 0.75, 0.55, 0.50);

\echo '--- Insert click for position 1 ---'
INSERT INTO clicks(impression_id, item_id, position, dwell_ms, open_type)
VALUES (:'impression_id', 'N_TEST_2', 1, 12000, 'same_tab');

\echo '--- Sanity check counts ---'
SELECT
  (SELECT COUNT(*) FROM impression_items WHERE impression_id = :'impression_id') AS shown_count,
  (SELECT COUNT(*) FROM clicks WHERE impression_id = :'impression_id') AS click_count;

\echo '--- Training-style join output ---'
SELECT
  ii.impression_id,
  ii.position,
  ii.item_id,
  i.title,
  CASE WHEN c.item_id IS NOT NULL THEN 1 ELSE 0 END AS clicked
FROM impression_items ii
JOIN items i ON i.item_id = ii.item_id
LEFT JOIN clicks c
  ON c.impression_id = ii.impression_id AND c.item_id = ii.item_id
WHERE ii.impression_id = :'impression_id'
ORDER BY ii.position;
