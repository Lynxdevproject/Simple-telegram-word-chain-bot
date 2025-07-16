from telegram.ext import ContextTypes
import random
from words import valid_words
from utils.session_data import game_sessions  # Pastikan lo pisah shared data

async def start_game_session(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    session = game_sessions.get(chat_id)
    if not session or not session["active"]:
        return

    # Ambil nama pemain
    name_list = []
    for player_id in session["players"]:
        try:
            user = await context.bot.get_chat(player_id)
            name_list.append(f"• {user.first_name}")
        except:
            name_list.append(f"• Player {player_id}")

    # Random kata awal dari kamus
    first_word = random.choice(list(valid_words))
    session["last_word"] = first_word
    session["used_words"].append(first_word)

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "🎮 *Game Sambung Kata Dimulai!*\n\n"
            "👥 *Pemain dalam sesi ini:*\n" +
            "\n".join(name_list) +
            f"\n\n🧠 *Kata pertama* : `{first_word}`\n"
            "↩️ *Balas pesan ini dengan kata sambungan yang valid!*"
        ),
        parse_mode="Markdown"
    )


async def announce_winner(chat_id: int, winner_id: int, session: dict, context: ContextTypes.DEFAULT_TYPE):
    try:
        winner = await context.bot.get_chat(winner_id)
        name = winner.first_name
    except:
        name = f"Player {winner_id}"

    total_words = len(session["used_words"])
    score = session["scores"].get(winner_id, 0)
    longest_word = max(session["used_words"], key=len) if session["used_words"] else "-"

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"🎉 *Yeay!* {name} memenangkan pertandingan!\n"
            f"🤓 Curiga dia Albert Einstein...\n\n"
            f"📦 *Kata ditebak*      : `{total_words}`\n"
            f"🎯 *Skor akhir*        : `{score}`\n"
            f"📏 *Kata terpanjang*   : `{longest_word}`\n\n"
            f"📊 Tekan `/leaderboard` untuk lihat ranking player!"
        ),
        parse_mode="Markdown"
    )
    game_sessions.pop(chat_id)
