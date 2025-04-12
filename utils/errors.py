def reply_error(update, user_message: str, error: Exception):
  update.message.reply_text(
    f"{user_message}\n\n<spoiler>{error}</spoiler>",
    parse_mode='HTML'
  )