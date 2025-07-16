import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from .game_handler import start_game_session  # Pastikan ini ada

game_sessions = {}
MIN_PLAYERS = 2
MAX_PLAYERS = 5

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_id = user.id
    group_name = update.effective_chat.title or "grup ini"

    # 🚪 Cek sesi lobi
    session = game_sessions.get(chat_id)
    if session and session.get("active"):
        await update.message.reply_text("⚠️ Game sedang berlangsung! Tunggu sesi selesai dulu.")
        return

    # 🆕 Buat session baru kalau belum ada
    if not session:
        game_sessions[chat_id] = {
            "players": [],
            "active": False,
            "scores": {},
            "used_words": [],
            "last_word": None
        }
        session = game_sessions[chat_id]

    if user_id in session["players"]:
        await update.message.reply_text("👀 Kamu sudah gabung! Tunggu pemain lain masuk.")
        return

    if len(session["players"]) >= MAX_PLAYERS:
        await update.message.reply_text("🚫 Room penuh! Maksimal pemain tercapai.")
        return

    session["players"].append(user_id)
    session["scores"][user_id] = 0

    await update.message.reply_text(
        f"✅ {user.first_name} telah bergabung di room *{group_name}*.\n👥 Total pemain: {len(session['players'])}",
        parse_mode="Markdown"
    )

    if len(session["players"]) > 1:
        await update.message.reply_text("🎉 Pemain baru telah bergabung!\nMakin banyak pemain, makin seru!")

    # 🎮 Auto-start game saat pemain minimal terpenuhi
    if len(session["players"]) == MIN_PLAYERS and not session["active"]:
        session["active"] = True
        await context.bot.send_message(
            chat_id=chat_id,
            text="✅ Jumlah pemain mencukupi!\nGame akan dimulai sekarang 🚀"
        )
        await start_game_session(chat_id, context)
