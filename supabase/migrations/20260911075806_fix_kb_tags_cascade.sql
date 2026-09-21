ALTER TABLE kb_tags DROP CONSTRAINT kb_tags_knowledge_base_id_fkey;

ALTER TABLE kb_tags
  ADD CONSTRAINT kb_tags_knowledge_base_id_fkey
  FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_base(id) ON DELETE CASCADE;