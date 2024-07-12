import logging 
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.filters import Command

from config import token
from database import Database

logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db = Database('sql.db')
db.create_table()

class Form(StatesGroup):
    username = State()
    
@dp.message(Command('start'))
async def start(message:Message, state: FSMContext):
    await state.set_state(Form.username)
    await message.reply("Привет! Как тебя зовут ?")
    
@dp.message(Form.username)
async def process_usernmae(message:Message, state: FSMContext):
    usernme = message.text
    db.add_user(message.from_user.id, usernme)
    await state.clear()
    await message.reply(f"Приятно познакомиться, {usernme}! ")

@dp.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    age = message.text
    user_data = await state.get_data()
    username = user_data['username']
    db.add_user(message.from_user.id, username, age)
    await state.clear()
    await message.reply(f"Приятно познакомиться, {username}! Тебе {age} лет.")

def get_back_button():
    back_button = types.InlineKeyboardButton(text="Назад", callback_data="back")
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[back_button]])
    return keyboard

@dp.callback_query(lambda c: c.data == 'back')
async def process_callback_back(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.set_state(Form.username)
    await bot.send_message(callback_query.from_user.id, "Привет! Как тебя зовут?")
    
@dp.message(Command('me'))
async def me(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        await message.reply(f"Ты зарегистрирован как {user[2]}")
    else:
        await message.reply(f"Ты еще не зарегистрирован")
        
   
async def on_startup():
    logging.info("Настройки базы")
    db.create_table()
    logging.info("База загружена")
        
async def main():
    dp.startup.register(on_startup)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())