from telegram import Update
from telegram.ext import ContextTypes
import random
from words import valid_words  # Lo tinggal isi isi kamus di sini

from .join_handler import game_sessions  # sharing data

async def game_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    session = game_sessions.get(chat_id)

    if not session or not session["active"]:
        await update.message.reply_text("⚠️ Belum ada sesi aktif atau pemain belum cukup.")
        return

    if "last_word" in session:
        await update.message.reply_text("⏳ Game sudah dimulai sebelumnya.")
        return

    # 🎯 Random kata awal
    first_word = random.choice(list(valid_words))
    session["last_word"] = first_word
    session["used_words"].append(first_word)

    # 📣 Ambil nama-nama pemain
    name_list = []
    for pid in session["players"]:
        try:
            user = await context.bot.get_chat(pid)
            name_list.append(f"• {user.first_name}")
        except:
            name_list.append(f"• Player {pid}")

    await update.message.reply_text(
        "🎮 *Game Sambung Kata Dimulai!*\n\n"
        "👥 *Pemain yang bergabung:*\n" +
        "\n".join(name_list) +
        f"\n\n🧠 *Kata pertama* : `{first_word}`\n"
        "↩️ *Balas pesan ini dengan kata sambungan yang valid!*",
        parse_mode="Markdown"
    )
