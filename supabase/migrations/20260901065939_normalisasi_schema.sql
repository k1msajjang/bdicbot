-- ============================================
-- 1. FIX kb_tags
-- ============================================
ALTER TABLE kb_tags ALTER COLUMN knowledge_base_id TYPE int8;
ALTER TABLE kb_tags DROP CONSTRAINT IF EXISTS kb_tags_pkey;
ALTER TABLE kb_tags ADD COLUMN IF NOT EXISTS id int4 GENERATED ALWAYS AS IDENTITY PRIMARY KEY;
ALTER TABLE kb_tags ADD CONSTRAINT unique_kb_tag UNIQUE (knowledge_base_id, tag_id);

-- ============================================
-- 2. kb_categories & kb_programs sama migrasi data lama
-- ============================================
CREATE TABLE kb_categories (
  id int4 GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  knowledge_base_id int8 NOT NULL REFERENCES knowledge_base(id) ON DELETE CASCADE,
  category_id int4 NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
  UNIQUE (knowledge_base_id, category_id)
);
INSERT INTO kb_categories (knowledge_base_id, category_id)
SELECT id, category_id FROM knowledge_base WHERE category_id IS NOT NULL;

CREATE TABLE kb_programs (
  id int4 GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  knowledge_base_id int8 NOT NULL REFERENCES knowledge_base(id) ON DELETE CASCADE,
  program_id int4 NOT NULL REFERENCES programs(id) ON DELETE RESTRICT,
  UNIQUE (knowledge_base_id, program_id)
);
INSERT INTO kb_programs (knowledge_base_id, program_id)
SELECT id, program_id FROM knowledge_base WHERE program_id IS NOT NULL;

-- ============================================
-- 3. BERSIHIN knowledge_base & users
-- ============================================
ALTER TABLE knowledge_base
  DROP COLUMN IF EXISTS category_id,
  DROP COLUMN IF EXISTS program_id,
  DROP COLUMN IF EXISTS edited_by,
  DROP COLUMN IF EXISTS updated_at;

ALTER TABLE users
  DROP COLUMN IF EXISTS created_by,
  DROP COLUMN IF EXISTS created_at;

-- ============================================
-- 4. ACTIVITY LOG
-- ============================================
CREATE TABLE activity_log (
  id int4 GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id int8 NOT NULL REFERENCES users(id),
  table_name text NOT NULL,
  record_id int8 NOT NULL,
  action text NOT NULL CHECK (action IN ('create', 'update', 'delete', 'activate', 'deactivate')),
  old_value jsonb,
  new_value jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- ============================================
-- 5. INDEX
-- ============================================
CREATE INDEX IF NOT EXISTS idx_kb_categories_category ON kb_categories (category_id);
CREATE INDEX IF NOT EXISTS idx_kb_programs_program ON kb_programs (program_id);
CREATE INDEX IF NOT EXISTS idx_kb_tags_tag ON kb_tags (tag_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_lookup ON activity_log (table_name, record_id);

-- ============================================
-- 6. RLS
-- ============================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;