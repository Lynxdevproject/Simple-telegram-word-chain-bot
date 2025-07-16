import asyncio
from telegram import Update
from telegram.ext import ContextTypes

game_sessions = {}
MIN_PLAYERS = 2
MAX_PLAYERS = 5
WAIT_TIME = 60  # detik

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
            "countdown_started": False,
            "scores": {},
            "used_words": []
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
        f"✅ {user.first_name} telah bergabung di room *{group_name}*.",
        parse_mode="Markdown"
    )

    if len(session["players"]) > 1:
        await update.message.reply_text("🎉 Pemain baru telah bergabung!\nMakin banyak pemain, makin seru!")

    # ⏳ Start countdown hanya sekali
    if not session["countdown_started"]:
        session["countdown_started"] = True
        await context.bot.send_message(
            chat_id=chat_id,
            text="⏳ *1 menit sebelum room dibatalkan!*\nAyo tekan /join kalau mau ikut!",
            parse_mode="Markdown"
        )
        await asyncio.sleep(WAIT_TIME)

        # ⌛ Evaluasi jumlah pemain
        if len(session["players"]) < MIN_PLAYERS:
            await context.bot.send_message(
                chat_id=chat_id,
                text="😢 Game dibatalkan karena pemain tidak mencukupi.\nCoba lagi nanti ya!"
            )
            game_sessions.pop(chat_id)
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"✅ Room siap! {len(session['players'])} pemain bergabung.\n"
                    "Silakan kirim kata pertama atau tunggu sistem giliran aktif 🎮"
                )
            )
            session["active"] = True
