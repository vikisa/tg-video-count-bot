from telegram import Update
from telegram.ext import CallbackContext
from datetime import date
from db.queries import (
  get_member_id_by_tg_id,
  get_active_marathon_id_for_user,
  has_already_submitted,
  is_user_ill_that_day,
  was_video_used_before,
  insert_day_result
)

def handle_video(update: Update, context: CallbackContext):
  user = update.effective_user
  video = update.message.video

  if not video:
    return

  tg_id = user.id
  today = date.today()
  file_unique_id = video.file_unique_id

  member_id = get_member_id_by_tg_id(tg_id)
  if not member_id:
    return

  marathon_id = get_active_marathon_id_for_user(member_id, today)
  if not marathon_id:
    return

  if is_user_ill_that_day(member_id, today):
    return

  if has_already_submitted(member_id, marathon_id, today):
    return

  reused = was_video_used_before(member_id, file_unique_id, today)

  insert_day_result(
    member_id, marathon_id, today,
    complete=True,
    reused_video=reused,
    video_id=file_unique_id
  )
