from telegram import Update
from telegram.ext import ContextTypes

# 🗂️ Simpan sesi game per grup
game_sessions = {}

MAX_PLAYERS = 5  # Bisa diubah nanti sesuai mode

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_id = user.id

    session = game_sessions.get(chat_id)

    if session and session.get("active"):
        await update.message.reply_text("⚠️ Game sedang berlangsung!\nTunggu sampai sesi selesai untuk bergabung.")
        return

    if not session:
        game_sessions[chat_id] = {
            "players": [],
            "active": False
        }

    if user_id in game_sessions[chat_id]["players"]:
        await update.message.reply_text("👀 Kamu sudah gabung! Tunggu host mulai game.")
        return

    if len(game_sessions[chat_id]["players"]) >= MAX_PLAYERS:
        await update.message.reply_text("🚫 Maksimal pemain telah tercapai.")
        return

    game_sessions[chat_id]["players"].append(user_id)
    await update.message.reply_text(f"✅ {user.first_name} telah bergabung!\n👥 Total pemain: {len(game_sessions[chat_id]['players'])}")
