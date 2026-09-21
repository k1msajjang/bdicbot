CREATE OR REPLACE FUNCTION create_user_account(
  p_username text,
  p_password_hash text,
  p_nama varchar,
  p_role_id int4,
  p_created_by int8
)
RETURNS int8
LANGUAGE plpgsql
AS $$
DECLARE
  v_new_id int8;
BEGIN
  INSERT INTO users (username, pw, nama, role_id, is_active)
  VALUES (p_username, p_password_hash, p_nama, p_role_id, true)
  RETURNING id INTO v_new_id;

  INSERT INTO activity_log (user_id, table_name, record_id, action, old_value, new_value)
  VALUES (
    p_created_by, 'users', v_new_id, 'create', NULL,
    jsonb_build_object('username', p_username, 'nama', p_nama, 'role_id', p_role_id, 'is_active', true)
  );

  RETURN v_new_id;
END;
$$;