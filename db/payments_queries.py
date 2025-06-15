from db.connect import get_conn

def insert_payment(marathon_id: int, member_id: int, payment: int):
  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute(
        """
        INSERT INTO payments (marathon_id, member_id, payment)
        VALUES (%s, %s, %s);
        """,
        (marathon_id, member_id, payment)
      )
    conn.commit()

def get_total_payments_by_member(marathon_id: int, member_id: int) -> int:
  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute("""
                  SELECT COALESCE(SUM(payment), 0)
                  FROM payments
                  WHERE marathon_id = %s AND member_id = %s;
                  """, (marathon_id, member_id))
      return cur.fetchone()[0]