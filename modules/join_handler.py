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
    group_name = update.effective_chat.title or "Grup Kamu"

    session = game_sessions.get(chat_id)

    if session and session.get("active"):
        await update.message.reply_text("⚠️ Game sedang berlangsung!\nTunggu sesi selesai dulu.")
        return

    if not session:
        game_sessions[chat_id] = {
            "players": [],
            "active": False,
            "countdown_started": False
        }

    players = game_sessions[chat_id]["players"]

    if user_id in players:
        await update.message.reply_text("👀 Kamu sudah gabung!\nTunggu pemain lain masuk.")
        return

    if len(players) >= MAX_PLAYERS:
        await update.message.reply_text("🚫 Room penuh! Maksimal pemain tercapai.")
        return

    players.append(user_id)
    await update.message.reply_text(
        f"✅ {user.first_name} telah bergabung ke room *{group_name}*.\n"
        f"👥 Total pemain: {len(players)}",
        parse_mode="Markdown"
    )

    if len(players) > 1:
        await update.message.reply_text("🎉 Pemain baru telah bergabung!\nMakin banyak, makin seru!")

    # ⏳ Mulai countdown 1x saja per session
    if not game_sessions[chat_id]["countdown_started"]:
        game_sessions[chat_id]["countdown_started"] = True
        await asyncio.sleep(WAIT_TIME)

        # ⌛ Evaluasi jumlah pemain setelah 1 menit
        if len(players) < MIN_PLAYERS:
            await context.bot.send_message(
                chat_id=chat_id,
                text="😢 Game dibatalkan karena pemain tidak mencukupi.\nAyo coba lagi nanti!"
            )
            game_sessions.pop(chat_id)
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"✅ Room siap! {len(players)} pemain terdaftar.\nSilakan kirim kata pertama untuk mulai game 🎮"
            )
            game_sessions[chat_id]["active"] = True
