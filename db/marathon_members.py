from db.connect import get_conn

def add_participant(marathon_id, member_id):
  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute("""
                  INSERT INTO marathon_members (marathon_id, member_id)
                  VALUES (%s, %s)
                      ON CONFLICT DO NOTHING
                  """, (marathon_id, member_id))
    conn.commit()

def remove_participant(marathon_id, member_id):
  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute("""
                  DELETE FROM marathon_members
                  WHERE marathon_id = %s AND member_id = %s
                  """, (marathon_id, member_id))
    conn.commit()

def count_participants(marathon_id):
  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute("SELECT COUNT(*) FROM marathon_members WHERE marathon_id = %s", (marathon_id,))
      return cur.fetchone()[0]

def get_participant_usernames(marathon_id):
  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute("""
                  SELECT m.username
                  FROM marathon_members mm
                           JOIN members m ON mm.member_id = m.id
                  WHERE mm.marathon_id = %s
                  """, (marathon_id,))
      return [row[0] for row in cur.fetchall()]

def is_member_of_marathon(marathon_id, member_id):
  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute("""
                  SELECT 1 FROM marathon_members
                  WHERE marathon_id = %s AND member_id = %s
                  """, (marathon_id, member_id))
      return bool(cur.fetchone())

def get_all_members_of_marathon(marathon_id):
  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute("""
                  SELECT m.id, m.tg_id, m.username
                  FROM marathon_members mm
                           JOIN members m ON mm.member_id = m.id
                  WHERE mm.marathon_id = %s
                  """, (marathon_id,))
      return [
        {"id": row[0], "tg_id": row[1], "username": row[2]}
        for row in cur.fetchall()
      ]
