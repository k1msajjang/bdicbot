CREATE OR REPLACE FUNCTION toggle_knowledge_base_status(
  p_id int8,
  p_new_status bool,
  p_user_id int8
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
  v_old_status bool;
  v_action text;
BEGIN
  SELECT status INTO v_old_status FROM knowledge_base WHERE id = p_id FOR UPDATE;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'Entry dengan id % tidak ditemukan', p_id;
  END IF;

  UPDATE knowledge_base SET status = p_new_status WHERE id = p_id;

  v_action := CASE WHEN p_new_status THEN 'activate' ELSE 'deactivate' END;

  INSERT INTO activity_log (user_id, table_name, record_id, action, old_value, new_value)
  VALUES (
    p_user_id, 'knowledge_base', p_id, v_action,
    jsonb_build_object('status', v_old_status),
    jsonb_build_object('status', p_new_status)
  );
END;
$$;