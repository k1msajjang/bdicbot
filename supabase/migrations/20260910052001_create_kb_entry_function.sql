CREATE OR REPLACE FUNCTION create_knowledge_base_entry(
  p_judul varchar,
  p_jawaban text,
  p_embedding vector(768),
  p_category_ids int4[],
  p_program_ids int4[],
  p_tag_ids int4[],
  p_user_id int8
)
RETURNS int8
LANGUAGE plpgsql
AS $$
DECLARE
  v_new_id int8;
  v_id int4;
BEGIN
  INSERT INTO knowledge_base (judul, jawaban, status, embedding)
  VALUES (p_judul, p_jawaban, false, p_embedding)
  RETURNING id INTO v_new_id;

  FOREACH v_id IN ARRAY p_category_ids LOOP
    INSERT INTO kb_categories (knowledge_base_id, category_id) VALUES (v_new_id, v_id);
  END LOOP;

  FOREACH v_id IN ARRAY p_program_ids LOOP
    INSERT INTO kb_programs (knowledge_base_id, program_id) VALUES (v_new_id, v_id);
  END LOOP;

  FOREACH v_id IN ARRAY p_tag_ids LOOP
    INSERT INTO kb_tags (knowledge_base_id, tag_id) VALUES (v_new_id, v_id);
  END LOOP;

  INSERT INTO activity_log (user_id, table_name, record_id, action, old_value, new_value)
  VALUES (
    p_user_id, 'knowledge_base', v_new_id, 'create', NULL,
    jsonb_build_object(
      'judul', p_judul, 'jawaban', p_jawaban, 'status', false,
      'category_ids', p_category_ids, 'program_ids', p_program_ids, 'tag_ids', p_tag_ids
    )
  );

  RETURN v_new_id;
END;
$$;