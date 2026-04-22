import asyncio
import sqlite3
import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import LabeledPrice

TOKEN = "ТВОЙ_ТОКЕН"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- БД ---
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    subscription_until TEXT
)
""")
conn.commit()

# --- МЕНЮ ---
def menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🎁 Пробник"), types.KeyboardButton(text="💎 VIP")],
            [types.KeyboardButton(text="📊 Статус")]
        ],
        resize_keyboard=True
    )

# --- START (ТВОЙ ТЕКСТ НЕ ТРОГАЛ) ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    text = (
        "🔥 Добро пожаловать туда, куда не пускают всех 🔥\n\n"
        "Думаешь, ты уже всё видел? Ошибаешься.\n"
        "В приватке ты узнаешь обо мне намного больше, чем остальные даже представить не могут.\n\n"
        "Тут нет случайных людей.\n"
        "Только те, кто реально хочет больше контента, больше меня, больше доступа.\n\n"
        "💎 Жёсткий эксклюзив\n"
        "💎 То, что не попадает в паблик\n\n"
        "Хочешь остаться обычным зрителем — листай дальше.\n"
        "Хочешь ближе — ты знаешь, что делать 👇\n\n"
        "📌 Доступ:\n"
        "— 7 дней — проверить, потянешь ли\n"
        "— 3 месяца — для тех, кто остаётся\n\n"
        "Нажимай и заходи.\n"
        "Но назад уже не так интересно 😈"
    )

    await msg.answer(text, reply_markup=menu())

# --- VIP МЕНЮ ---
@dp.message(lambda m: m.text == "💎 VIP")
async def vip_menu(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="3 дня"), types.KeyboardButton(text="3 месяца")],
            [types.KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )

    await msg.answer("💎 Выбери тариф:", reply_markup=kb)

# --- ⭐ 3 ДНЯ ---
@dp.message(lambda m: m.text == "3 дня")
async def vip_3_days(msg: types.Message):
    await bot.send_invoice(
        chat_id=msg.chat.id,
        title="VIP 3 дня",
        description="Доступ к приватному контенту",
        payload="vip_3_days",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="VIP 3 дня", amount=1)]
    )

# --- ⭐ 3 МЕСЯЦА ---
@dp.message(lambda m: m.text == "3 месяца")
async def vip_3_months(msg: types.Message):
    await bot.send_invoice(
        chat_id=msg.chat.id,
        title="VIP 3 месяца",
        description="Полный доступ к приватному контенту",
        payload="vip_3_months",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="VIP 3 месяца", amount=500)]
    )

# --- ОПЛАТА ---
@dp.pre_checkout_query()
async def pre_checkout(query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(lambda m: m.successful_payment)
async def success(msg: types.Message):
    payload = msg.successful_payment.invoice_payload

    if payload == "vip_3_days":
        until = datetime.datetime.now() + datetime.timedelta(days=3)

    elif payload == "vip_3_months":
        until = datetime.datetime.now() + datetime.timedelta(days=90)

    else:
        return

    cursor.execute(
        "INSERT OR REPLACE INTO users VALUES (?, ?)",
        (msg.from_user.id, until.isoformat())
    )
    conn.commit()

    link = "https://t.me/+EIzZleRPZrE0ZGUx"

    await msg.answer(
        f"✅ Оплата прошла!\n"
        f"📅 Доступ до: {until}\n\n"
        f"🔐 Твоя приватка:\n{link}"
    )
# --- СТАТУС ---
@dp.message(lambda m: m.text == "📊 Статус")
async def status(msg: types.Message):
    cursor.execute(
        "SELECT subscription_until FROM users WHERE user_id=?",
        (msg.from_user.id,)
    )
    row = cursor.fetchone()

    if not row:
        await msg.answer("❌ Подписки нет")
        return

    until = datetime.datetime.fromisoformat(row[0])

    if until > datetime.datetime.now():
        await msg.answer(f"✅ Активна до: {until}")
    else:
        await msg.answer("❌ Подписка истекла")

# --- RUN ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
