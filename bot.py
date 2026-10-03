import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# ========== الإعدادات ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
WEBAPP_URL = "https://mayarayq-svg.github.io/awv-app/"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton(
            text="🚀 Open AWV",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome = (
        "🎉 *Welcome to AWV!*\n\n"
        "💰 *Mining Game - Earn Crypto*\n\n"
        "📌 *How to play:*\n"
        "• Buy mining vehicles\n"
        "• Collect your AWV daily\n"
        "• Invite friends & earn 0.02 AWV each\n"
        "• Withdraw to your TON wallet\n\n"
        "🚀 *Tap the button below to start:*"
    )

    await update.message.reply_text(
        welcome,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN missing!")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("✅ Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
