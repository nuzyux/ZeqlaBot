import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Add your channel ID here or in .env

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Language selection keyboard
language_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
language_keyboard.add(
    KeyboardButton("English"),
    KeyboardButton("Русский"),
    KeyboardButton("O‘zbek")
)

# Questions per language
questions = {
    "English": [
        "Name of Business:",
        "Business Contact Information (Phone, Email, IG, etc):",
        "Business Location (Address or Map Pin):",
        "Personal Contact Information of Manager/Owner:",
        "Short Description of the Business:"
    ],
    "Русский": [
        "Название бизнеса:",
        "Контактная информация бизнеса (Телефон, Email, IG и т.д.):",
        "Местоположение бизнеса (Адрес или метка на карте):",
        "Личная контактная информация менеджера/владельца:",
        "Краткое описание бизнеса:"
    ],
    "O‘zbek": [
        "Biznes nomi:",
        "Biznes kontakt ma’lumotlari (Telefon, Email, IG va hokazo):",
        "Biznes manzili (Manzil yoki xaritada joylashuvi):",
        "Rahbar/egasining shaxsiy kontakt ma’lumotlari:",
        "Biznes haqida qisqa tavsif:"
    ]
}

thank_you_message = {
    "English": "Thank you for connecting with Zeqla. Your business will be listed in 1–2 business days.",
    "Русский": "Спасибо за подключение к Zeqla. Ваш бизнес будет добавлен в течение 1–2 рабочих дней.",
    "O‘zbek": "Zeqla bilan bog‘langaningiz uchun rahmat. Biznesingiz 1–2 ish kuni ichida joylashtiriladi."
}

user_data = {}
user_language = {}

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Please select your language / Пожалуйста, выберите язык / Iltimos, tilni tanlang:", reply_markup=language_keyboard)

@dp.message_handler(lambda message: message.text in ["English", "Русский", "O‘zbek"])
async def language_handler(message: types.Message):
    lang = message.text
    user_language[message.from_user.id] = lang
    user_data[message.from_user.id] = {"answers": [], "step": 0}
    await message.answer(questions[lang][0], reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(lambda message: message.from_user.id in user_data)
async def process_answers(message: types.Message):
    user_id = message.from_user.id
    lang = user_language[user_id]
    data = user_data[user_id]

    data["answers"].append(message.text)
    data["step"] += 1

    if data["step"] < len(questions[lang]):
        await message.answer(questions[lang][data["step"]])
    else:
        await message.answer(thank_you_message[lang])

        # --- Forward collected info to Telegram channel ---
        summary = f"""
Business Name: {data['answers'][0]}
Business Contact Info: {data['answers'][1]}
Business Location: {data['answers'][2]}
Owner/Manager Contact: {data['answers'][3]}
Short Description: {data['answers'][4]}
"""
        await bot.send_message(chat_id=CHANNEL_ID, text=summary)
        # ---------------------------------------------------

        user_data.pop(user_id)
        user_language.pop(user_id)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
