import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import aiohttp

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
WEBAPP_URL = "https://mayarayq-svg.github.io/awv-app/"
SUPABASE_URL = "https://geepmianewmjkttbnqkl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdlZXBtaWFuZXdtamt0dGJucWtsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTA5NjU1ODIsImV4cCI6MjEwNjU0MTU4Mn0.Fv5DtKqIcNDyK1ifzZ-f_35-zjqOa8Wlq4IT7PXP5QM"

# ⚠️ ضع معرفك هنا (ID تيليجرام) لتكون أنت الوحيد الذي يمكنه البث
ADMIN_ID = 0  # ← غيّر هذا إلى رقمك

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def get_main_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text="🚀 Open AWV",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_main_keyboard()
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
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📚 *AWV Help*\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - This message\n"
        "/invite - Get your invite link\n\n"
        "*How to earn:*\n"
        "1️⃣ Buy vehicles\n"
        "2️⃣ Collect earnings\n"
        "3️⃣ Invite friends (0.02 AWV each)\n"
        "4️⃣ Withdraw to TON\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def invite_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    invite_link = f"https://t.me/AWVEARNBot/awv?startapp=ref_{user_id}"
    text = (
        f"🔗 *Your invite link:*\n\n"
        f"`{invite_link}`\n\n"
        f"💰 Earn *0.02 AWV* for each friend!"
    )
    await update.message.reply_text(
        text,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

# ==========================================
# 📢 BROADCAST - إرسال رسالة لكل المستخدمين
# ==========================================
async def get_all_user_ids():
    """جلب كل معرّفات المستخدمين من Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/users?select=telegram_id"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [u["telegram_id"] for u in data]
    except Exception as e:
        print(f"Error fetching users: {e}")
    return []

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الأمر: /broadcast <الرسالة>"""
    user_id = update.effective_user.id

    # تحقق من صلاحية المشرف
    if ADMIN_ID != 0 and user_id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return

    # الحصول على الرسالة
    if not context.args:
        await update.message.reply_text(
            "📢 *How to use:*\n\n"
            "`/broadcast Your message here`\n\n"
            "The message will be sent to all users with the Open AWV button.",
            parse_mode="Markdown"
        )
        return

    message_text = " ".join(context.args)

    # إشعار البدء
    status_msg = await update.message.reply_text(
        "📢 *Broadcasting...*\n\nPlease wait...",
        parse_mode="Markdown"
    )

    # جلب المستخدمين
    user_ids = await get_all_user_ids()

    if not user_ids:
        await status_msg.edit_text("❌ No users found.")
        return

    # إرسال لكل مستخدم
    success = 0
    failed = 0
    keyboard = get_main_keyboard()

    for uid in user_ids:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"📢 *Announcement*\n\n{message_text}",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            success += 1
            # تأخير بسيط لتجنب الحظر من تيليجرام
            await asyncio.sleep(0.05)
        except Exception as e:
            failed += 1
            print(f"Failed to send to {uid}: {e}")

    # تقرير
    await status_msg.edit_text(
        f"✅ *Broadcast complete!*\n\n"
        f"• Sent: {success}\n"
        f"• Failed: {failed}\n"
        f"• Total: {len(user_ids)}",
        parse_mode="Markdown"
    )

async def main_async():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN missing!")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("invite", invite_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast_cmd))
    print("✅ Bot running...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    stop_signal = asyncio.Event()
    await stop_signal.wait()

def main():
    try:
        asyncio.run(main_async())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")

if __name__ == "__main__":
    main()
