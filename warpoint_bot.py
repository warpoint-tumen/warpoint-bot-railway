
import logging
import os
import random
import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")

tasks = [
    "📞 Обзвон электриков (5 встреч)",
    "🤝 Встреча с инженером по пожарной безопасности",
    "🧹 Подмести полы в зоне отдыха"
]

tasks_status = {i + 1: "не начато" for i in range(len(tasks))}
completed_history = []
evaluation_log = []
future_tasks = []

motivational_quotes = [
    "Даже самая длинная дорога начинается с первого шага.",
    "Сегодняшние усилия — это завтрашние победы!",
    "Каждый день — шанс стать лучше, чем вчера."
]

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ваш chat_id: {update.effective_chat.id}")
    keyboard = [
        ["📋 Задачи на сегодня", "📆 Завтра"],
        ["🤖 AI-режим", "📊 Статистика"],
        ["➕ Добавить задачу", "⭐ Оценить день"],
        ["ℹ️ Справка"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет, Тумэн Баярович! Я снова с тобой 💪", reply_markup=reply_markup)

async def tasks_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.date.today().strftime("%d.%m.%Y")
    msg = f"📋 Задачи на сегодня ({today}):\n"
    for i, task in enumerate(tasks, 1):
        msg += f"{i}. {task} — [{tasks_status[i]}]\n"
    await update.message.reply_text(msg)

async def show_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if future_tasks:
        msg = "📆 План на завтра:\n"
        for i, task in enumerate(future_tasks, 1):
            msg += f"{i}. {task}\n"
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("План на завтра пока не составлен.")

async def show_ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(motivational_quotes)
    done = sum(1 for s in tasks_status.values() if s == "выполнено")
    total = len(tasks)
    percent = int(done / total * 100) if total else 0
    await update.message.reply_text(f"🧠 Мотивация: {quote}\nСегодня: {done}/{total} задач ({percent}%)")

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    done = sum(1 for _, _ in completed_history)
    postponed = sum(1 for s in tasks_status.values() if s == "перенесено")
    in_progress = sum(1 for s in tasks_status.values() if s == "в процессе")
    await update.message.reply_text(f"📊 Статистика:\n✅ Выполнено: {done}\n🔁 Перенесено: {postponed}\n🟡 В процессе: {in_progress}")

async def update_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip().lower()
    if msg == "📋 задачи на сегодня":
        await tasks_today(update, context)
        return
    if msg == "📆 завтра":
        await show_tomorrow(update, context)
        return
    if msg == "🤖 ai-режим":
        await show_ai_mode(update, context)
        return
    if msg == "📊 статистика":
        await show_stats(update, context)
        return
    if msg == "➕ добавить задачу":
        await update.message.reply_text("Напиши новую задачу в формате: /v_zavtra Текст задачи")
        return
    if msg == "⭐ оценить день":
        await update.message.reply_text("Оцени день по шкале от 1 до 5:")
        return
    if msg == "ℹ️ справка":
        await update.message.reply_text("Доступные команды:\n/tasks — задачи на сегодня\n/zavtra — план на завтра\n/ai — AI-режим\n/stats — статистика\n/v_zavtra [текст] — добавить задачу на завтра")
        return

    parts = msg.split("-")
    if len(parts) == 2:
        try:
            num = int(parts[0].strip())
            action = parts[1].strip()
            if num in tasks_status:
                if "начал" in action:
                    tasks_status[num] = "в процессе"
                elif "готово" in action:
                    tasks_status[num] = "выполнено"
                    completed_history.append((datetime.datetime.now(), tasks[num - 1]))
                elif "перенос" in action:
                    tasks_status[num] = "перенесено"
                await update.message.reply_text(f"Обновлено: {num}. {tasks[num - 1]} — [{tasks_status[num]}]")
        except:
            pass

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), update_status))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
