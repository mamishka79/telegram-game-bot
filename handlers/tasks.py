from aiogram import types, Router, F
from utils.storage import load_data, save_data

task_router = Router()

user_progress = load_data()
waiting_for_task = {}
waiting_for_completion = {}

@task_router.message(F.text == "✍ Ввести задание")
async def input_task(message: types.Message):
    user_id = str(message.from_user.id)
    waiting_for_task[user_id] = True
    await message.answer("📝 Введите задание, которое вы хотите выполнить:")

@task_router.message(F.text == "✅ Завершить задачу")
async def complete_task(message: types.Message):
    user_id = str(message.from_user.id)
    tasks_list = user_progress.get(user_id, {"tasks": []})["tasks"]
    if not tasks_list:
        await message.answer("📋 У вас нет задач для завершения.")
        return
    waiting_for_completion[user_id] = True
    await message.answer("📝 Введите номер задачи, которую хотите отметить как выполненную:")

@task_router.message()
async def handle_task_input(message: types.Message):
    user_id = str(message.from_user.id)

    # Проверяем, не является ли сообщение одной из команд-кнопок
    if message.text in ["📊 Мой прогресс", "📩 Оставить отзыв", "📋 Список задач", "✅ Завершить задачу"]:
        return  # Передаем обработку дальше, не перехватываем это сообщение

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
                user_progress[user_id]["points"] += 10
                await message.answer(f"✅ Задача \"{task['description']}\" отмечена как выполненная. Вы заработали +10 очков!")
            save_data(user_progress)
        waiting_for_completion[user_id] = False
        return

    await message.answer("⚠️ Используйте кнопки для взаимодействия с ботом.")