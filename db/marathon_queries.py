from db.connect import get_conn
from datetime import datetime, timedelta

def save_marathon(name, chat_id, start_date, duration_days, penalty, created_by):
  # Преобразуем строку в дату
  start = datetime.strptime(start_date, "%d.%m.%Y")
  end = start + timedelta(days=duration_days - 1)

  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute("""
                  INSERT INTO marathons (name, chat_id, start_date, end_date, price, created_by)
                  VALUES (%s, %s, %s, %s, %s, %s)
                      RETURNING id
                  """, (name, chat_id, start.date(), end.date(), penalty, created_by))
      marathon_id = cur.fetchone()[0]
    conn.commit()
  return marathon_id

def get_active_marathon_by_chat(chat_id):
  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute("""
                  SELECT id, name, start_date, end_date, price
                  FROM marathons
                  WHERE chat_id = %s
                  ORDER BY id DESC
                      LIMIT 1
                  """, (chat_id,))
      row = cur.fetchone()
      if row:
        return {
          "id": row[0],
          "name": row[1],
          "start_date": row[2],
          "end_date": row[3],
          "price": row[4]
        }
      return None

def set_marathon_message_id(marathon_id, message_id):
  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute("UPDATE marathons SET message_id = %s WHERE id = %s", (message_id, marathon_id))
    conn.commit()