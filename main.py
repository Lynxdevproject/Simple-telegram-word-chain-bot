from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)

# Import dari handler modular
from handlers import join, check_word, leaderboard

import os

# 🔑 Token dari BotFather (atau ambil via env)
BOT_TOKEN = os.environ.get("BOT_TOKEN") or "ISI_TOKEN_DISINI"

# 🚀 Build bot app
app = Application.builder().token(BOT_TOKEN).build()

# 🔧 Registrasi Handler
app.add_handler(CommandHandler("join", join))           # untuk masuk lobi
app.add_handler(CommandHandler("leaderboard", leaderboard))  # lihat ranking
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_word))  # respon kata

# 🔛 Mulai polling
if __name__ == "__main__":
    print("🚀 WordChainBot aktif! Siap sambung kata!")
    app.run_polling()
