-- ============================================
-- UPDATE (full replace + reset status + regenerate junction table)
-- ============================================
CREATE OR REPLACE FUNCTION update_knowledge_base_entry(
  p_id int8,
  p_judul varchar,
  p_jawaban text,
  p_embedding vector(768),
  p_category_ids int4[],
  p_program_ids int4[],
  p_tag_ids int4[],
  p_user_id int8
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
  v_old_judul varchar;
  v_old_jawaban text;
  v_old_status bool;
  v_old_category_ids int4[];
  v_old_program_ids int4[];
  v_old_tag_ids int4[];
  v_id int4;
BEGIN
  SELECT judul, jawaban, status INTO v_old_judul, v_old_jawaban, v_old_status
  FROM knowledge_base WHERE id = p_id FOR UPDATE;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'Entry dengan id % tidak ditemukan', p_id;
  END IF;

  SELECT COALESCE(array_agg(category_id), '{}') INTO v_old_category_ids FROM kb_categories WHERE knowledge_base_id = p_id;
  SELECT COALESCE(array_agg(program_id), '{}') INTO v_old_program_ids FROM kb_programs WHERE knowledge_base_id = p_id;
  SELECT COALESCE(array_agg(tag_id), '{}') INTO v_old_tag_ids FROM kb_tags WHERE knowledge_base_id = p_id;

  UPDATE knowledge_base
  SET judul = p_judul, jawaban = p_jawaban, status = false, embedding = p_embedding
  WHERE id = p_id;

  DELETE FROM kb_categories WHERE knowledge_base_id = p_id;
  DELETE FROM kb_programs WHERE knowledge_base_id = p_id;
  DELETE FROM kb_tags WHERE knowledge_base_id = p_id;

  FOREACH v_id IN ARRAY p_category_ids LOOP
    INSERT INTO kb_categories (knowledge_base_id, category_id) VALUES (p_id, v_id);
  END LOOP;
  FOREACH v_id IN ARRAY p_program_ids LOOP
    INSERT INTO kb_programs (knowledge_base_id, program_id) VALUES (p_id, v_id);
  END LOOP;
  FOREACH v_id IN ARRAY p_tag_ids LOOP
    INSERT INTO kb_tags (knowledge_base_id, tag_id) VALUES (p_id, v_id);
  END LOOP;

  INSERT INTO activity_log (user_id, table_name, record_id, action, old_value, new_value)
  VALUES (
    p_user_id, 'knowledge_base', p_id, 'update',
    jsonb_build_object('judul', v_old_judul, 'jawaban', v_old_jawaban, 'status', v_old_status,
      'category_ids', v_old_category_ids, 'program_ids', v_old_program_ids, 'tag_ids', v_old_tag_ids),
    jsonb_build_object('judul', p_judul, 'jawaban', p_jawaban, 'status', false,
      'category_ids', p_category_ids, 'program_ids', p_program_ids, 'tag_ids', p_tag_ids)
  );
END;
$$;

-- ============================================
-- DELETE (permanen, snapshot lengkap ke log sebelum hilang)
-- ============================================
CREATE OR REPLACE FUNCTION delete_knowledge_base_entry(
  p_id int8,
  p_user_id int8
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
  v_judul varchar;
  v_jawaban text;
  v_status bool;
  v_category_ids int4[];
  v_program_ids int4[];
  v_tag_ids int4[];
BEGIN
  SELECT judul, jawaban, status INTO v_judul, v_jawaban, v_status
  FROM knowledge_base WHERE id = p_id FOR UPDATE;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'Entry dengan id % tidak ditemukan', p_id;
  END IF;

  SELECT COALESCE(array_agg(category_id), '{}') INTO v_category_ids FROM kb_categories WHERE knowledge_base_id = p_id;
  SELECT COALESCE(array_agg(program_id), '{}') INTO v_program_ids FROM kb_programs WHERE knowledge_base_id = p_id;
  SELECT COALESCE(array_agg(tag_id), '{}') INTO v_tag_ids FROM kb_tags WHERE knowledge_base_id = p_id;

  INSERT INTO activity_log (user_id, table_name, record_id, action, old_value, new_value)
  VALUES (
    p_user_id, 'knowledge_base', p_id, 'delete',
    jsonb_build_object('judul', v_judul, 'jawaban', v_jawaban, 'status', v_status,
      'category_ids', v_category_ids, 'program_ids', v_program_ids, 'tag_ids', v_tag_ids),
    NULL
  );

  DELETE FROM knowledge_base WHERE id = p_id;  -- junction table ikut kehapus otomatis (CASCADE)
END;
$$;