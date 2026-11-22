import os
import asyncio
import tempfile
from contextlib import asynccontextmanager

from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from yt_dlp import YoutubeDL

TOKEN = os.getenv(“BOT_TOKEN”)

bot = Bot(token=TOKEN) if TOKEN else None
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
await message.answer(
“Привет! ❤️ Пришли мне ссылку на фото или видео.”
)

@dp.message()
async def download(message: Message):
url = message.text or “”

if not url.startswith(("https://", "http://")):
    await message.answer("Пришли, пожалуйста, ссылку.")
    return
await message.answer("⏳ Пробую скачать...")
try:
    with tempfile.TemporaryDirectory() as folder:
        options = {
            "outtmpl": folder + "/%(title).80s.%(ext)s",
            "format": "best[ext=mp4]/best",
            "max_filesize": 45_000_000,
            "quiet": True,
            "noplaylist": True,
        }
        def download_file():
            with YoutubeDL(options) as ydl:
                ydl.download([url])
        await asyncio.to_thread(download_file)
        files = os.listdir(folder)
        if not files:
            await message.answer("Не удалось скачать файл.")
            return
        path = os.path.join(folder, files[0])
        with open(path, "rb") as file:
            await message.answer_document(file)
except Exception:
    await message.answer(
        "Не удалось скачать. Возможно, ссылка недоступна."
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
if bot:
task = asyncio.create_task(dp.start_polling(bot))
yield
await dp.stop_polling()
task.cancel()
await bot.session.close()
else:
yield

app = FastAPI(lifespan=lifespan)

@app.get(”/”)
async def home():
return {“status”: “Bot is running”}
