
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Firebase setup
cred = credentials.Certificate("warpointbot-firebase-adminsdk-fbsvc-4977f09b54.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
TASKS_COLLECTION = "tasks"

TOKEN = os.getenv("TOKEN")

def fetch_tasks():
    docs = db.collection(TASKS_COLLECTION).stream()
    return {doc.id: doc.to_dict().get("status", "не начато") for doc in docs}

def add_task(text, status="не начато"):
    db.collection(TASKS_COLLECTION).document(text).set({"status": status})

def update_task_status(task_text, status):
    db.collection(TASKS_COLLECTION).document(task_text).update({"status": status})

def format_task_list(tasks):
    if not tasks:
        return "Нет задач."
    return "\n".join([f"{i}. {task} — [{status}]" for i, (task, status) in enumerate(tasks.items(), 1)])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📋 Задачи", "➕ Добавить задачу"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет, Тумэн Баярович! Я читаю задачи из Firebase 🧠", reply_markup=markup)

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = fetch_tasks()
    await update.message.reply_text(format_task_list(tasks))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()

    if msg == "📋 Задачи":
        await list_tasks(update, context)
        return

    if msg == "➕ Добавить задачу":
        await update.message.reply_text("Напиши новую задачу в формате: /добавить Текст задачи")
        return

    if msg.startswith("/добавить "):
        text = msg.replace("/добавить ", "").strip()
        if text:
            add_task(text)
            await update.message.reply_text(f"Задача добавлена: {text}")
        return

    if "-" in msg:
        try:
            num, action = msg.split("-")
            num = int(num.strip())
            action = action.strip().lower()
            tasks = list(fetch_tasks().items())
            key = tasks[num - 1][0]
            if "начал" in action:
                update_task_status(key, "в процессе")
            elif "готово" in action:
                update_task_status(key, "выполнено")
            elif "перенос" in action:
                update_task_status(key, "перенесено")
            await update.message.reply_text(f"Статус задачи обновлён: {key}")
        except:
            await update.message.reply_text("Не удалось обновить задачу. Проверь формат.")
        return

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Ошибка: {context.error}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_error_handler(error)
    print("Бот запущен с Firebase...")
    app.run_polling()

if __name__ == "__main__":
    main()
