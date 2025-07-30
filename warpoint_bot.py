import os
import firebase_admin
from firebase_admin import credentials, db
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://warpointbot-default-rtdb.firebaseio.com'
})

def get_tasks():
    ref = db.reference("tasks/2025-07-30")
    return ref.get() or {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, Тумэн Баярович! Я читаю задачи из Firebase 🧠")

async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = get_tasks()
    if not tasks:
        await update.message.reply_text("Задачи на сегодня не найдены.")
        return
    msg = "📝 Задачи на сегодня (30.07.2025):"
"
    for i, (key, value) in enumerate(tasks.items(), 1):
        msg += f"{i}. {value['text']} — [{value['status']}]
"
    await update.message.reply_text(msg)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("задачи", tasks))
    app.run_polling()

if __name__ == "__main__":
    main()
