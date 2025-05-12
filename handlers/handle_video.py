from telegram import Update
from telegram.ext import CallbackContext
from db.marathon_queries import get_active_marathon_by_chat
from db.member_queries import get_member_by_tg_id
from db.marathon_members import is_member_of_marathon
from db.day_results import save_day_result

from datetime import date

def handle_video(update: Update, context: CallbackContext):
  chat = update.effective_chat
  user = update.effective_user
  video = update.message.video

  # проверяем, что это группа
  if chat.type not in ["group", "supergroup"]:
    return

  marathon = get_active_marathon_by_chat(chat.id)
  if not marathon:
    return  # нет марафона — игнорим

  member = get_member_by_tg_id(user.id)
  if not member:
    return  # не зарегистрирован

  if not is_member_of_marathon(marathon["id"], member["id"]):
    return  # не участник этого марафона

  # фиксируем
  save_day_result(
    member_id=member["id"],
    marathon_id=marathon["id"],
    current_date=date.today(),
    video_unique_id=video.file_unique_id
  )
