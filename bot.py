import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os
import asyncio

# Получаем ключи из переменных окружения
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

def generate_translation(text: str) -> str:
    """
    Переводит текст: если русский — на татарский, если татарский — на русский.
    Без предварительного определения языка.
    """
    prompt = (
        "Ты — переводчик с русского на татарский и с татарского на русский. "
        "Если текст на русском — переведи его на татарский. Если текст на татарском — переведи на русский. "
        "Текст для перевода:\n\n" + text
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # или "gpt-3.5-turbo" для экономии
            messages=[
                {"role": "system", "content": "Ты — двунаправленный переводчик русского и татарского."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.3,
            n=1,
        )
        translation = response['choices'][0]['message']['content'].strip()
        return translation
    except Exception as e:
        print(f"Error generating translation: {e}")
        return "Произошла ошибка при переводе. Попробуйте позже."

async def send_message_in_parts(update: Update, text: str):
    max_length = 4096
    while len(text) > max_length:
        await update.message.reply_text(text[:max_length])
        text = text[max_length:]
        await asyncio.sleep(0.3)
    if text:
        await update.message.reply_text(text)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Привет! Отправь мне текст на русском или татарском — я переведу его на другой язык."
    )

async def translate(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    print(f"Received text: {text}")

    await update.message.chat.send_action("typing")

    translation = generate_translation(text)
    print(f"Generated translation: {translation}")

    await send_message_in_parts(update, translation)

def main():
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate))

    application.run_polling(allowed_updates=["message"])

if __name__ == "__main__":
    main()
