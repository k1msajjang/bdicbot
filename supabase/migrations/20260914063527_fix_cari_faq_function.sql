DROP FUNCTION IF EXISTS cari_faq(vector(768), int);

CREATE FUNCTION cari_faq(query_embedding vector(768), match_count int DEFAULT 3)
RETURNS TABLE (
  id int8,
  judul varchar,
  jawaban text
)
LANGUAGE sql
AS $$
  SELECT id, judul, jawaban
  FROM knowledge_base
  WHERE status = true
  ORDER BY embedding <=> query_embedding
  LIMIT match_count;
$$;