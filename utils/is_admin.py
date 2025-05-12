from db.member_queries import get_member_by_tg_id

def is_admin(telegram_id):
  user = get_member_by_tg_id(telegram_id)
  return user is not None and user['is_admin'] is True