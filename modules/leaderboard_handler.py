from telegram import Update
from telegram.ext import ContextTypes
from utils.session_data import game_sessions

# Simpan skor global (bisa pakai DB kalau mau upgrade nanti)
global_scores = {}

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    session = game_sessions.get(chat_id)

    if not session or "scores" not in session:
        await update.message.reply_text("❌ Belum ada data sesi skor.")
        return

    # 🔁 Update skor global
    for uid, score in session["scores"].items():
        global_scores[uid] = max(global_scores.get(uid, 0), score)

    # 📊 Ambil nama-nama pemain
    leaderboard_text = "📊 *Papan Peringkat WordChain:*\n\n"
    sorted_scores = sorted(global_scores.items(), key=lambda x: x[1], reverse=True)

    for rank, (uid, score) in enumerate(sorted_scores[:10], 1):
        try:
            user = await context.bot.get_chat(uid)
            name = user.first_name
        except:
            name = f"User {uid}"
        leaderboard_text += f"{rank}. {name} — `{score}` poin\n"

    await update.message.reply_text(leaderboard_text, parse_mode="Markdown")
