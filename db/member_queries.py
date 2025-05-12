from db.connect import get_conn

def get_member_by_tg_id(tg_id: int):
  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute('SELECT id, tg_id, is_admin FROM members WHERE tg_id = %s', (tg_id,))
      row = cur.fetchone()
      if row:
        return {
          'id': row[0],
          'tg_id': row[1],
          'is_admin': row[2]
        }
      return None

def create_member(tg_id, username, is_admin=False):
  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute("""
                  INSERT INTO members (tg_id, username, is_admin)
                  VALUES (%s, %s, %s)
                      ON CONFLICT (tg_id) DO NOTHING
                  """, (tg_id, username, is_admin))
    conn.commit()

def remove_member(tg_id):
  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute("""
                  DELETE FROM members
                  WHERE tg_id = %s
                  """, (tg_id))
    conn.commit()

def get_member_id_by_username(username: str):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("SELECT id FROM members WHERE username = %s", (username,))
  result = cursor.fetchone()
  conn.close()
  return result[0] if result else None

def set_admin_by_username(username):
  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute("UPDATE members SET is_admin = true WHERE username = %s", (username,))
      if cur.rowcount == 0:
        return False
    conn.commit()
  return True
