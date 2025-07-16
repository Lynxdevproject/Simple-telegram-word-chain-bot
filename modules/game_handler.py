from telegram import Update
from telegram.ext import ContextTypes, filters
from words import valid_words
from utils.session_data import game_sessions
import random, asyncio

MAX_SCORE = 30
TIME_LIMIT = 30  # detik

# 🚀 Start Game Session
async def start_game_session(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    session = game_sessions.get(chat_id)
    if not session or not session["active"]:
        return

    name_list = []
    for player_id in session["players"]:
        try:
            user = await context.bot.get_chat(player_id)
            name_list.append(f"• {user.first_name}")
        except:
            name_list.append(f"• Player {player_id}")

    first_word = random.choice(list(valid_words))
    session["last_word"] = first_word
    session["used_words"].append(first_word)
    session["current_turn"] = 0
    session["waiting_for"] = session["players"][0]

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "🎮 *Game Dimulai!*\n\n"
            "👥 *Pemain:*\n" + "\n".join(name_list) +
            f"\n\n🧠 *Kata pertama* : `{first_word}`\n"
            f"⏳ *Giliran*: {name_list[0]}\nBalas dalam 30 detik!",
        parse_mode="Markdown"
    )

    await start_timer(chat_id, context)


# 🔁 Timer per Giliran
async def start_timer(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    session = game_sessions.get(chat_id)
    if not session or not session["active"]:
        return

    user_id = session["waiting_for"]
    await asyncio.sleep(TIME_LIMIT)

    # ⌛ Jika belum diganti → gugur
    if session.get("waiting_for") == user_id:
        try:
            user = await context.bot.get_chat(user_id)
            name = user.first_name
        except:
            name = f"Player {user_id}"

        await context.bot.send_message(chat_id, text=f"⛔ {name} tidak menjawab. Gugur!")

        session["players"].remove(user_id)
        session["scores"].pop(user_id, None)

        if len(session["players"]) < 2:
            await context.bot.send_message(chat_id, text="😢 Game berakhir karena pemain tidak mencukupi.")
            game_sessions.pop(chat_id)
            return

        await next_turn(chat_id, context)


# 🔄 Ganti Giliran
async def next_turn(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    session = game_sessions.get(chat_id)
    if not session or not session["active"]:
        return

    players = session["players"]
    turn = session["current_turn"]
    session["current_turn"] = (turn + 1) % len(players)
    session["waiting_for"] = players[session["current_turn"]]

    try:
        user = await context.bot.get_chat(session["waiting_for"])
        name = user.first_name
    except:
        name = f"Player {session['waiting_for']}"

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"⏳ *Giliran*: {name}\nKata sambung dari huruf `{session['last_word'][-1]}`",
        parse_mode="Markdown"
    )

    await start_timer(chat_id, context)


# ✅ Check Kata Balasan
async def check_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()
    session = game_sessions.get(chat_id)

    if not session or not session["active"] or user_id not in session["players"]:
        return

    if user_id != session["waiting_for"]:
        await update.message.reply_text("⛔ Bukan giliran kamu!")
        return

    if text not in valid_words:
        await update.message.reply_text("❌ Kata tidak ditemukan di kamus.")
        return

    if text in session["used_words"]:
        await update.message.reply_text("🔁 Kata sudah digunakan.")
        return

    if session["last_word"][-1] != text[0]:
        await update.message.reply_text(f"❌ Kata harus dimulai dengan huruf `{session['last_word'][-1]}`", parse_mode="Markdown")
        return

    # ✅ Kata valid
    session["last_word"] = text
    session["used_words"].append(text)
    session["scores"][user_id] += 1
    session["waiting_for"] = None  # biar timer tahu udah dijawab

    await update.message.reply_text(f"✅ Kata diterima! Skor kamu: {session['scores'][user_id]}")

    if session["scores"][user_id] >= MAX_SCORE or len(session["used_words"]) >= MAX_SCORE:
        await announce_winner(chat_id, user_id, session, context)
    else:
        await next_turn(chat_id, context)


# 🏆 Pengumuman Pemenang
async def announce_winner(chat_id: int, winner_id: int, session: dict, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = await context.bot.get_chat(winner_id)
        name = user.first_name
    except:
        name = f"Player {winner_id}"

    total_words = len(session["used_words"])
    score = session["scores"].get(winner_id, 0)
    longest = max(session["used_words"], key=len)

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"🎉 *Yeay!* {name} memenangkan pertandingan!\n"
            f"🤓 Curiga dia Albert Einstein...\n\n"
            f"📦 *Kata ditebak*      : `{total_words}`\n"
            f"🎯 *Skor akhir*        : `{score}`\n"
            f"📏 *Kata terpanjang*   : `{longest}`\n\n"
            "📊 Ketik `/leaderboard` untuk lihat papan peringkat!"
        ),
        parse_mode="Markdown"
    )
    game_sessions.pop(chat_id)
