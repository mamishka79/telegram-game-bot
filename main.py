from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from config import TOKEN
from handlers import tasks, progress
from utils.storage import load_data, save_data
import asyncio

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_progress = load_data()

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
    await message.answer("Привет! Это бот для управления временем в игровой форме. Начнем?", reply_markup=game_keyboard)

tasks.register_handlers(dp)
progress.register_handlers(dp)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
