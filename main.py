from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import asyncio
import json
import os

DATA_FILE = "db.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

TOKEN = "7285975428:AAHqWZR4h1KVWS3pztMq5nljhKD0bfZPyM0"  # Вставьте ваш токен от BotFather
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Загружаем сохранённые данные пользователей или создаём пустой словарь
user_progress = load_data()
waiting_for_task = {}         # Флаги ожидания ввода задания
waiting_for_completion = {}   # Флаги ожидания ввода номера задачи для завершения

# Клавиатура с игровыми действиями
game_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✍ Ввести задание")],
        [KeyboardButton(text="📋 Список задач")],
        [KeyboardButton(text="✅ Завершить задачу")],
        [KeyboardButton(text="📊 Мой прогресс")],
        [KeyboardButton(text="📩 Оставить отзыв")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id not in user_progress:
        user_progress[user_id] = {"points": 0, "tasks": []}
        save_data(user_progress)
    waiting_for_task[user_id] = False
    waiting_for_completion[user_id] = False
    await message.answer("Привет! Это бот для управления временем в игровой форме. Начнем?", reply_markup=game_keyboard)

@dp.message(F.text == "✍ Ввести задание")
async def input_task(message: types.Message):
    user_id = str(message.from_user.id)
    waiting_for_task[user_id] = True  # Устанавливаем ожидание ввода нового задания
    await message.answer("📝 Введите задание, которое вы хотите выполнить:")

@dp.message(F.text == "📋 Список задач")
async def list_tasks(message: types.Message):
    user_id = str(message.from_user.id)
    tasks_list = user_progress.get(user_id, {"tasks": []})["tasks"]
    if not tasks_list:
        await message.answer("📋 У вас нет сохранённых задач.")
        return
    response = "📋 Ваши задачи:\n"
    for i, task in enumerate(tasks_list, start=1):
        response += f"{i}. {task['description']} - {task['status']}\n"
    await message.answer(response)

@dp.message(F.text == "✅ Завершить задачу")
async def complete_task(message: types.Message):
    user_id = str(message.from_user.id)
    tasks_list = user_progress.get(user_id, {"tasks": []})["tasks"]
    if not tasks_list:
        await message.answer("📋 У вас нет задач для завершения.")
        return
    waiting_for_completion[user_id] = True  # Ожидаем ввода номера задачи для завершения
    await message.answer("📝 Введите номер задачи, которую хотите отметить как выполненную:")

@dp.message(F.text == "📊 Мой прогресс")
async def show_progress(message: types.Message):
    user_id = str(message.from_user.id)
    progress = user_progress.get(user_id, {"points": 0, "tasks": []})
    completed_count = sum(1 for t in progress["tasks"] if t["status"] == "выполнен")
    await message.answer(f"📈 Ваш прогресс:\n✅ Задач выполнено: {completed_count}\n🏆 Очков: {progress['points']}")

@dp.message(F.text == "📩 Оставить отзыв")
async def leave_feedback(message: types.Message):
    await message.answer("📢 Напишите ваш отзыв прямо в этот чат, и мы его учтем!")

@dp.message()
async def handle_message(message: types.Message):
    user_id = str(message.from_user.id)

    # Если бот ожидает ввода нового задания
    if waiting_for_task.get(user_id, False):
        task_description = message.text.strip()
        if task_description:
            user_progress[user_id]["tasks"].append({
                "description": task_description,
                "status": "в прогрессе"
            })
            waiting_for_task[user_id] = False
            save_data(user_progress)
            await message.answer("✅ Задание сохранено! Статус: в прогрессе.")
        else:
            await message.answer("⚠️ Задание не может быть пустым.")
        return

    # Если бот ожидает ввода номера задачи для завершения
    if waiting_for_completion.get(user_id, False):
        try:
            index = int(message.text.strip())
        except ValueError:
            await message.answer("⚠️ Пожалуйста, введите корректный номер задачи.")
            return

        tasks_list = user_progress.get(user_id, {"tasks": []})["tasks"]
        if index < 1 or index > len(tasks_list):
            await message.answer("⚠️ Задача с таким номером не найдена.")
        else:
            task = tasks_list[index-1]
            if task["status"] == "выполнен":
                await message.answer("⚠️ Эта задача уже выполнена.")
            else:
                task["status"] = "выполнен"
                user_progress[user_id]["points"] += 10  # Начисляем очки за выполнение задачи
                await message.answer(f"✅ Задача \"{task['description']}\" отмечена как выполненная. Вы заработали +10 очков!")
            save_data(user_progress)
        waiting_for_completion[user_id] = False
        return

    # Если никакое ожидание не активно — предлагаем использовать кнопки
    await message.answer("⚠️ Используйте кнопки для взаимодействия с ботом.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
