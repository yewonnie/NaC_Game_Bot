import os
import sqlite3

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from NaC_Bot import start_game_with_bot, set_difficulty, process_move_bot
from NaC_Friend import start_game_with_friend, process_move_friend


load_dotenv()

bot = Bot(os.getenv("TOKEN_BOT"))
dp = Dispatcher(bot)

db = sqlite3.connect("NaCGame.db")
cursor = db.cursor()


@dp.message_handler(commands=["start"])
async def greeting_message(message: types.Message):
    await registration(message)  # сохраняем пользователя в бд

    # берём username бота
    bot_user = await message.bot.get_me()
    bot_username = bot_user.username

    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Добавить Бота в группу", url=f"https://t.me/{bot_username}?startgroup=true"))

    if message.chat.type == "private":  # лс
        await message.answer(
            f"Привет, {message.from_user.full_name}!\n"
            "Это приветственное сообщение в лс с ботом",
            reply_markup=kb
        )
    else:  # в группе
        await message.answer(
            f"Привет!\n"
            "Это приветственное сообщение в группе",
        )


@dp.message_handler(commands=['leaderboard'])
async def get_users_score(message: types.Message):
    await registration(message)

    leaders_list = [i for i in cursor.execute("SELECT * FROM users ORDER BY score DESC")]

    leaderboard_text = f"Топ-10 игроков:\n"  # можно изменить количество человек в топе, только потом ещё поменять срез
    current_rank = 0
    prev_score = None
    user_score = 0
    user_rank = 0
    top_10 = []

    for i, player in enumerate(leaders_list, start=1):
        if player[3] != prev_score:
            current_rank += 1
            prev_score = player[3]
        top_10.append([current_rank, player[1], player[3]])  # место в топе, имя, кол-во очков

        if player[0] == message.from_user.id:  # если игрок, вызывающий команду, есть в топе
            user_score = player[3]
            user_rank = current_rank

    for player in top_10[:10]:  # все остальные игроки не из топа
        leaderboard_text += f"{player[0]}. {player[1]} — {player[2]} 🪙\n"  # место в топе, имя, кол-во очков

    # дополнительная строка для игрока, вызывающего команду
    leaderboard_text += f"\nВаш счёт:\n{user_rank}. {message.from_user.full_name} — {user_score} 🪙"

    await message.answer(leaderboard_text)


@dp.message_handler(commands=['game_with_friend'])
async def game_with_friend(message: types.Message):
    await registration(message)
    await start_game_with_friend(message)


@dp.message_handler(commands=['game_with_bot'])
async def game_with_bot(message: types.Message):
    await registration(message)
    await start_game_with_bot(message)


async def registration(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = f"@{message.from_user.username}"

    # ищем человека в бд по имени и/или по username
    info_id = cursor.execute("SELECT * FROM users WHERE id=?", (user_id, )).fetchone()
    info_username = (
        cursor.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if username != "@None" else None
    )

    if info_id is None and info_username is None:  # если ничего не нашлось, то добавляем в бд
        user_data = (user_id, full_name, username, 0)
        cursor.execute("INSERT INTO users (id, full_name, username, score) VALUES (?, ?, ?, ?)", user_data)
        db.commit()
    else:  # если такой человек уже зарегистрирован, то обновляем его данные, если были изменены
        if info_id is not None:
            if info_id[1] != full_name:
                cursor.execute("UPDATE users SET full_name=? WHERE id=?", (full_name, user_id, ))
                db.commit()
            if info_id[2] != username:
                cursor.execute("UPDATE users SET username=? WHERE id=?", (username, user_id, ))
                db.commit()


@dp.callback_query_handler(lambda c: c.data.startswith("difficulty_"))
async def set_difficulty_bot(callback: types.CallbackQuery):
    await set_difficulty(callback)


@dp.callback_query_handler(lambda c: c.data.startswith("bot_"))
async def process_bot_move(callback: types.CallbackQuery):
    await process_move_bot(callback)


@dp.callback_query_handler(lambda c: c.data.startswith("friend_"))
async def process_friend_move(callback: types.CallbackQuery):
    await process_move_friend(callback)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
