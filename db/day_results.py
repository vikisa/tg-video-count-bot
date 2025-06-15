from db.connect import get_conn

def save_day_result(member_id, marathon_id, current_date, video_unique_id):
  reused = False

  with get_conn() as conn:
    with conn.cursor() as cur:
      # проверка на повтор видео
      cur.execute("""
                  SELECT 1 FROM day_results
                  WHERE video_unique_id = %s
                  """, (video_unique_id,))
      if cur.fetchone():
        reused = True

      # попытка вставки результата
      try:
        cur.execute("""
                    INSERT INTO day_results (member_id, marathon_id, date, complete, reused_video, video_unique_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (member_id, marathon_id, date) DO NOTHING
                    """, (member_id, marathon_id, current_date, True, reused, video_unique_id))
        conn.commit()
      except Exception as e:
        print(f"[day_results error] {e}")

def get_members_who_sent_video(marathon_id, selected_date):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT member_id FROM day_results
                WHERE marathon_id = %s AND date = %s AND complete = TRUE
            """, (marathon_id, selected_date))
            return {row[0] for row in cur.fetchall()}

def count_missed_days_for_member(marathon_id: int, member_id: int, total_days: int, start_date, end_date) -> int:
  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute("""
                  SELECT COUNT(DISTINCT date)
                  FROM day_results
                  WHERE marathon_id = %s AND member_id = %s AND complete = TRUE AND date BETWEEN %s AND %s;
                  """, (marathon_id, member_id))
      sent_days = cur.fetchone()[0] or 0

      return total_days - sent_days
