from db.connect import get_conn
from datetime import date

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