import random
import asyncio
import sqlite3

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import RetryAfter


user_games_friend = {}
db = sqlite3.connect("NaCGame.db")
cursor = db.cursor()


class NaCGameFriend:
    def __init__(self, player1_name, player2_name, player1_id, player2_id, player1, player2, chat_id, game_id, game_name):
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.player1 = player1  # переменная, сохраняющая ссылку на акк первого игрока
        self.player2 = player2  # переменная, сохраняющая ссылку на акк второго игрока
        self.chat_id = chat_id
        self.game_id = game_id  # переменная, сохраняющая "идентификатор" игры для правильной работы программы
        self.game_name = game_name  # вторая похожая переменная, сохраняющая "идентификатор" игры для правильной работы программы
        self.current_player = random.choice([self.player1_name, self.player2_name])
        self.player1_symbol, self.player2_symbol = random.sample(["❌", "⭕️"], k=2)
        self.game_area = self._create_board()
        self.game_message_id = None  # сообщение с игровым полем
        self.is_processing = False  # переменная необходимая для правильного чередования ходов игроков

    @staticmethod
    def _create_board():
        return InlineKeyboardMarkup(row_width=3).add(*[
            InlineKeyboardButton("⬜️", callback_data=f"friend_{i}") for i in range(1, 10)
        ])

    def check_winner(self):
        board = [btn.text for row in self.game_area.inline_keyboard for btn in row]
        win_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]

        for combo in win_combinations:
            if board[combo[0]] == board[combo[1]] == board[combo[2]] != "⬜️":
                winner = self.player1_name if board[combo[0]] == self.player1_name else self.player2_name
                return True, winner

        return (False, None) if "⬜️" in board else (False, "draw")

    def __repr__(self):
        """
        метод для вывода информации для отладки
        """
        return ("NaCGameFriend"
                f"(player1_name='{self.player1_name}', "
                f"player2_name='{self.player2_name}', "
                f"player1_id='{self.player1_id}', "
                f"player2_id='{self.player2_id}', "
                f"player1_symbol='{self.player1_symbol}', "
                f"player2_symbol='{self.player2_symbol}', "
                f"game_message_id='{self.game_message_id}', "
                f"game_id='{self.game_id}', "
                f"game_name='{self.game_name}', "
                f"chat_id='{self.chat_id}')")


async def start_game_with_friend(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Укажите соперника через пробел:\n/game_with_friend @ИМЯ")
        return

    player2_name = ""
    player2_id = ""
    bot_user = await message.bot.get_me()
    bot_username = bot_user.username

    for entity in message.entities:
        if entity.type == "text_mention":  # если у человека нет username, то записываем его по id
            player2_id = str(entity.user.id)
            player2_name = entity.user.full_name
        else:  # в противном случае по его username
            player2_name, player2_id = args[1], args[1]

    # ищем такого человека по одному из совпадений
    info_id = cursor.execute("SELECT * FROM users WHERE id=?", (int(player2_id), )).fetchone() if player2_id.isdigit() else None
    info_username = cursor.execute("SELECT * FROM users WHERE username=?", (player2_name, )).fetchone()

    # сохраняем пользователя, если он не найдем в бд и если у него нет username
    if player2_id.isdigit() and info_username is None and info_id is None:
        user_data = (player2_id, player2_name, "@None", 0)
        cursor.execute("INSERT INTO users (id, full_name, username, score) VALUES (?, ?, ?, ?)", user_data)
        db.commit()
    elif info_id is not None or info_username is not None:
        pass
    else:  # если человека нет в бд и у него есть username, то просим его сделать другое действие, чтобы записать его в бд
        await message.answer(
            f"Пусть {player2_name} пока поиграет с ботом"  # например поиграть с ботом
        )
        return

    player1_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    player1_id = str(message.from_user.id)

    if player2_name.lower() == f"@{bot_username.lower()}":
        await message.answer("Для игры с ботом используйте /game_with_bot")
        return

    if player1_name.lower() == player2_name.lower() or player1_id == player2_id:
        await message.answer("Нельзя играть с самим собой!")
        return

    sorted_players_id = sorted([player1_id, player2_id])
    sorted_players_name = sorted([player1_name, player2_name])
    game_id = f"{sorted_players_id[0]}_{sorted_players_id[1]}"
    game_name = f"{sorted_players_name[0]}_{sorted_players_name[1]}"
    chat_id = str(message.chat.id)

    if chat_id in user_games_friend and (game_id in user_games_friend[chat_id] or game_name in user_games_friend[chat_id]):
        await message.answer("Игра между этими участниками уже существует!")
        return

    player1 = player1_name if player1_name.startswith("@") else f"<a href='tg://user?id={int(player1_id)}'>{player1_name}</a>"
    player2 = player2_name if player2_name.startswith("@") else f"<a href='tg://user?id={int(player2_id)}'>{player2_name}</a>"

    game = NaCGameFriend(player1_name, player2_name, player1_id, player2_id, player1, player2, chat_id, game_id, game_name)
    # записываем два "идентификационных" значения для текущеё игры
    user_games_friend.setdefault(game.chat_id, {})[game.game_id] = game
    user_games_friend.setdefault(game.chat_id, {})[game.game_name] = game

    move_text = (
        f"Игра между {game.player1} {game.player1_symbol} "
        f"и {game.player2} {game.player2_symbol}\n\n"
        f"Сейчас ходит: {game.current_player}"
    )

    sent_message = await message.answer(move_text, reply_markup=game.game_area)
    game.game_message_id = sent_message.message_id


async def process_move_friend(callback: types.CallbackQuery):
    position = int(callback.data.replace("friend_", ""))

    chat_id = str(callback.message.chat.id)
    player_id = str(callback.from_user.id)
    player_name = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name

    # далее идёт проверка на то, кто пытается играть и на каком поле
    game = None
    if chat_id in user_games_friend:
        for game_in_chat in user_games_friend[chat_id].values():
            if callback.message.message_id != game_in_chat.game_message_id:
                continue

            if (player_id in [game_in_chat.player1_id, game_in_chat.player2_id] or
                player_name in [game_in_chat.player1_name, game_in_chat.player2_name]):
                game = game_in_chat
                break

    if not game:
        await callback.answer("Игра не найдена или завершена!")
        return

    if callback.message.message_id != game.game_message_id:
        await callback.answer("Нельзя сделать ход на этом поле!")  # нельзя нажать на игровое сообщение чужого игрока
        return

    if game.is_processing:
        await callback.answer()  # пустое сообщение при переходе хода
        return

    if game.current_player != player_name:
        await callback.answer(f"⌛ Сейчас ходит {game.current_player}!")  # если в момент хода соперника нажать на поле
        return

    game.is_processing = True

    btn_index = position - 1
    row, col = divmod(btn_index, 3)
    btn = game.game_area.inline_keyboard[row][col]

    try:
        if btn.text != "⬜️":
            await callback.answer("Эта клетка уже занята!")
            return

        current_symbol = game.player1_symbol if player_name == game.player1_name else game.player2_symbol
        btn.text = current_symbol

        has_winner, winner = game.check_winner()
        if has_winner:
            await handle_game_over_friend(callback, game, winner)
            return
        elif winner == "draw":  # ничья
            await handle_game_over_friend(callback, game, "draw")
            return

        game.current_player = game.player2_name if game.current_player == game.player1_name else game.player1_name

        await update_game_message(callback, game)
        await callback.answer()

    except RetryAfter as e:
        await callback.answer(str(e))
        await asyncio.sleep(e.timeout)
        await process_move_friend(callback)
    finally:
        game.is_processing = False


async def update_game_message(callback: types.CallbackQuery, game: NaCGameFriend):
    """
    удобная функция для автоматического обновления текста сообщения "кто сейчас ходит"
    """
    msg = (
        f"Игра между {game.player1} {game.player1_symbol} "
        f"и {game.player2} {game.player2_symbol}\n\n"
        f"Сейчас ходит: {game.current_player}"
    )
    return await callback.message.edit_text(msg, reply_markup=game.game_area)


def update_user_score(user_id, username, score_update):
    if score_update == 0:  # если ничья
        try:  # выводим по id
            return cursor.execute("SELECT score FROM users WHERE id=?", (int(user_id),)).fetchone()[0]
        except ValueError:  # в противном случае по username
            return cursor.execute("SELECT score FROM users WHERE username=?", (username,)).fetchone()[0]

    try:  # выводим по id
        cursor.execute(
            "UPDATE users SET score = CASE WHEN score + ? > 0 THEN score + ? ELSE 0 END WHERE id = ?",
            (score_update, score_update, int(user_id))
        )
        db.commit()
        return cursor.execute("SELECT score FROM users WHERE id=?", (int(user_id),)).fetchone()[0]
    except ValueError:  # в противном случае по username
        cursor.execute(
            "UPDATE users SET score = CASE WHEN score + ? > 0 THEN score + ? ELSE 0 END WHERE username = ?",
            (score_update, score_update, username)
        )
        db.commit()
        return cursor.execute("SELECT score FROM users WHERE username=?", (username,)).fetchone()[0]


async def handle_game_over_friend(callback: types.CallbackQuery, game: NaCGameFriend, winner: str):
    if winner == "draw":
        result_text = f"Ничья!"

        score_update1 = 0
        score_update2 = 0
    else:
        result_text = f"Победитель: {winner}!"

        score_update1 = 4 if game.player1_name == winner else -4
        score_update2 = 4 if game.player2_name == winner else -4

    user_score1 = update_user_score(game.player1_id, game.player1_name, score_update1)
    user_score2 = update_user_score(game.player2_id, game.player2_name, score_update2)

    # финальный результат доски
    board = "\n".join(
        " ".join(btn.text for btn in row)
        for row in game.game_area.inline_keyboard
    )

    final_message = (
        f"{result_text}\n\n"
        f"Игра между:\n"
        f"{game.player1} ({user_score1} 🪙) {game.player1_symbol} vs {game.player2} ({user_score2} 🪙) {game.player2_symbol}\n\n"
        f"{board}\n\n"
        f"Новая игра:\n/game_with_friend @ИМЯ"
    )

    await callback.message.edit_text(final_message, parse_mode="HTML")

    if game.chat_id in user_games_friend:
        chat_games = user_games_friend[game.chat_id]

        for key in [game.game_id, game.game_name]:
            if key in chat_games:
                del chat_games[key]  # если идентификационный ключ нашёлся в chat_games, то удаляем его, так как игра закончилась

        # если в каком-либо чате закончились все игры, то удаляем чат из словаря
        if not chat_games:
            del user_games_friend[game.chat_id]
