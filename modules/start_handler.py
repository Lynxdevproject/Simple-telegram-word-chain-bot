from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = context.bot_data.get("username", "your_bot")
    url_invite = f"https://t.me/{username}?startgroup=true"
    url_dev = "https://t.me/itsmelynxs"  # Ganti kalau lo punya link khusus

    keyboard = [
        [InlineKeyboardButton("➕ Tambahkan ke Grup", url=url_invite)],
        [InlineKeyboardButton("🛠 Developer", url=url_dev)]
    ]

    await update.message.reply_text(
        "🎮 *Hi!* Aku adalah game PvP *WordChainBot*!\n\n"
        "Aku bisa bantu kamu bermain sambung kata dalam Bahasa Inggris biar grup jadi makin hidup 🗣🔥\n"
        "Ketik `/join` untuk masuk game, lalu host bisa mulai dengan `/startgame`\n"
        "Sambungkan kata sesuai huruf terakhir, rebut skor, dan jadi juara vokab!\n\n"
        "Ayo tambahkan aku ke grup dan ajak teman kamu main bareng ✨",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
