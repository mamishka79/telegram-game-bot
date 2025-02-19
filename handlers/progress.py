from aiogram import types, Router, F
from utils.storage import load_data

progress_router = Router()
user_progress = load_data()

@progress_router.message(F.text == "📊 Мой прогресс")
async def show_progress(message: types.Message):
    user_id = str(message.from_user.id)
    progress = user_progress.get(user_id, {"points": 0, "tasks": []})
    completed_count = sum(1 for t in progress["tasks"] if t["status"] == "выполнен")
    await message.answer(f"📈 Ваш прогресс:\n✅ Задач выполнено: {completed_count}\n🏆 Очков: {progress['points']}")

def register_handlers(dp):
    dp.include_router(progress_router)