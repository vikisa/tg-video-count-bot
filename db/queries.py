from db.connect import get_conn
from datetime import date

def insert_marathon(name, start_date, end_date, price):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("""
        INSERT INTO marathons (name, start_date, end_date, price)
        VALUES (%s, %s, %s, %s)
    """, (name, start_date, end_date, price))
  conn.commit()
  conn.close()


def get_or_create_member(tg_id, username):
  conn = get_conn()
  cursor = conn.cursor()

  # Пытаемся найти участника
  cursor.execute("SELECT id FROM members WHERE tg_id = %s", (tg_id,))
  row = cursor.fetchone()

  if row:
    member_id = row[0]
  else:
    # Вставляем нового
    cursor.execute(
      "INSERT INTO members (tg_id, username) VALUES (%s, %s) RETURNING id",
      (tg_id, username)
    )
    member_id = cursor.fetchone()[0]
    conn.commit()

  conn.close()
  return member_id

def get_marathon_id_and_start(name):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("SELECT id, start_date FROM marathons WHERE name = %s", (name,))
  result = cursor.fetchone()
  conn.close()
  return result  # (id, start_date)

def add_member_to_marathon(member_id, marathon_id, joined_date):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("""
        INSERT INTO marathon_members (user_id, marathon_id, joined_date)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING
    """, (member_id, marathon_id, joined_date))
  conn.commit()
  conn.close()

def get_member_id_by_username(username: str):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("SELECT id FROM members WHERE name = %s", (username,))
  result = cursor.fetchone()
  conn.close()
  return result[0] if result else None

def add_illness(user_id: int, start_date: date, day_count: int):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute(
    "INSERT INTO ills (user_id, start_date, day_count) VALUES (%s, %s, %s)",
    (user_id, start_date, day_count)
  )
  conn.commit()
  conn.close()

def is_admin(tg_id: int) -> bool:
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("SELECT is_admin FROM members WHERE tg_id = %s", (tg_id,))
  result = cursor.fetchone()
  conn.close()
  return result and result[0]

def get_member_id_by_tg_id(tg_id):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("SELECT id FROM members WHERE tg_id = %s", (tg_id,))
  row = cursor.fetchone()
  conn.close()
  return row[0] if row else None

def get_active_marathon_id_for_user(member_id, today):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("""
        SELECT m.id
        FROM marathons m
        JOIN marathon_members mm ON mm.marathon_id = m.id
        WHERE mm.user_id = %s
          AND m.start_date <= %s AND m.end_date >= %s
        LIMIT 1
    """, (member_id, today, today))
  row = cursor.fetchone()
  conn.close()
  return row[0] if row else None

def get_active_marathon_id_for_user(member_id, today):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("""
        SELECT m.id
        FROM marathons m
        JOIN marathon_members mm ON mm.marathon_id = m.id
        WHERE mm.user_id = %s
          AND m.start_date <= %s AND m.end_date >= %s
        LIMIT 1
    """, (member_id, today, today))
  row = cursor.fetchone()
  conn.close()
  return row[0] if row else None

def is_user_ill_that_day(member_id, day):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("""
        SELECT 1 FROM ills
        WHERE user_id = %s
          AND start_date <= %s
          AND (start_date + (day_count * INTERVAL '1 day')) > %s
    """, (member_id, day, day))
  result = cursor.fetchone()
  conn.close()
  return bool(result)

def has_already_submitted(member_id, marathon_id, day):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("""
        SELECT 1 FROM day_results
        WHERE member_id = %s AND marathon_id = %s AND date = %s
    """, (member_id, marathon_id, day))
  result = cursor.fetchone()
  conn.close()
  return bool(result)

def was_video_used_before(member_id, unique_id, today):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("""
        SELECT 1 FROM day_results
        WHERE member_id = %s AND video_unique_id = %s AND date != %s
    """, (member_id, unique_id, today))
  result = cursor.fetchone()
  conn.close()
  return bool(result)

def insert_day_result(member_id, marathon_id, day, complete, reused_video, video_id):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("""
        INSERT INTO day_results
        (member_id, marathon_id, date, complete, reused_video, video_unique_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (member_id, marathon_id, day, complete, reused_video, video_id))
  conn.commit()
  conn.close()

def get_marathon_id_by_name(name):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("SELECT id FROM marathons WHERE name = %s", (name,))
  row = cursor.fetchone()
  conn.close()
  return row[0] if row else None

def get_marathon_participants(marathon_id):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("""
        SELECT m.id, m.name
        FROM members m
        JOIN marathon_members mm ON mm.user_id = m.id
        WHERE mm.marathon_id = %s
    """, (marathon_id,))
  result = cursor.fetchall()
  conn.close()
  return result  # список (id, name)

def get_members_who_submitted(marathon_id, target_date):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("""
        SELECT member_id FROM day_results
        WHERE marathon_id = %s AND date = %s AND complete = TRUE
    """, (marathon_id, target_date))
  rows = cursor.fetchall()
  conn.close()
  return set(r[0] for r in rows)

def get_members_ill_that_day(target_date):
  conn = get_conn()
  cursor = conn.cursor()
  cursor.execute("""
        SELECT user_id FROM ills
        WHERE start_date <= %s AND (start_date + day_count * INTERVAL '1 day') > %s
    """, (target_date, target_date))
  rows = cursor.fetchall()
  conn.close()
  return set(r[0] for r in rows)
