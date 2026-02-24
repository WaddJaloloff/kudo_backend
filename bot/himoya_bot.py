from json import load
import os
import telebot
from telebot import types
import sys
from telebot.types import InputMediaPhoto
import django
from django.utils import timezone
import logging
load.env()  # .env faylidan o'zgaruvchilarni yuklash

# Loyihaning root folderini path ga qo‘shish
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kudo_backend.settings")

django.setup()

from core.models import TelegramFoydalanuvchi, TasdiqlovchiKod

# Logger sozlamasi
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ADMIN_ID = 6565325969  # admin telegram id
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"), parse_mode="HTML")

user_states = {}

# /start handler
@bot.message_handler(commands=['start'])
def start(message):
    logging.info(f"/start called by {message.from_user.id}")
    user = TelegramFoydalanuvchi.objects.filter(telegram_id=message.from_user.id).first()

    if user and user.telefon_raqam:
        logging.info("User has phone number, skipping phone request")
        user_states[message.chat.id] = {"step": "id"}
        bot.send_message(message.chat.id, "🔎 Mahsulot ID sini kiriting:")
    else:
        logging.info("User has no phone number, requesting phone")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton("📱 Telefon raqam yuborish", request_contact=True)
        markup.add(btn)
        bot.send_message(
            message.chat.id,
            "Assalomu alaykum 👋\nMahsulotni tekshirish uchun telefon raqamingizni yuboring:",
            reply_markup=markup
        )

# Telefon raqam handler
@bot.message_handler(content_types=['contact'])
def get_phone(message):
    logging.info(f"Contact received from {message.from_user.id}: {message.contact.phone_number}")
    contact = message.contact

    user, created = TelegramFoydalanuvchi.objects.get_or_create(
        telegram_id=message.from_user.id,
        defaults={
            "telegram_username": f"@{message.from_user.username}",
            "telefon_raqam": contact.phone_number
        }
    )

    if not created:
        user.telefon_raqam = contact.phone_number
        user.save()
        logging.info("Existing user phone updated")

    # Tugmani yashirish uchun oddiy usul: bo'sh keyboard yuboramiz
    bot.send_message(
        message.chat.id,
        "Telefon raqamingiz qabul qilindi ✅",
        reply_markup=types.ReplyKeyboardRemove()
    )

    user_states[message.chat.id] = {"step": "id"}
    bot.send_message(message.chat.id, "🔎 Endi mahsulot ID sini kiriting:")

# Mahsulot ID handler
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get("step") == "id")
def get_id(message):
    logging.info(f"ID received from {message.from_user.id}: {message.text.strip()}")
    user_states[message.chat.id] = {
        "step": "code",
        "id": message.text.strip()
    }

    bot.send_message(message.chat.id, "🔐 6 xonali kodni kiriting:")

# Mahsulot kod handler
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get("step") == "code")
def get_code(message):
    code = message.text.strip()
    logging.info(f"Code received from {message.from_user.id}: {code}")

    try:
        # 6 xonali kodni bazadan topamiz, faqat ishlatilmagan kodlar orasidan
        kod = TasdiqlovchiKod.objects.select_related('tasdiqlovchi_set__mahsulot').get(
            code=code,
            ishlatilgan=False
        )

        user = TelegramFoydalanuvchi.objects.get(
            telegram_id=message.from_user.id
        )

        # Kodni ishlatildi deb belgilaymiz
        kod.ishlatilgan = True
        kod.tekshirgan_user = user
        kod.tekshirilgan_vaqti = timezone.now()
        kod.save()
        logging.info(f"Code validated successfully: {code}")

        # Mahsulotni olamiz
        mahsulot = kod.tasdiqlovchi_set.mahsulot

        # Asosiy rasm va xususiyatlar
        asosiy_rasm = mahsulot.rasmlar.filter(asosiy=True).first() or mahsulot.rasmlar.first()
        xususiyatlar = "\n".join([f"• {x.sarlavha}" for x in mahsulot.xususiyatlar.all()]) or "Hozircha bo'sh"

        caption_text = (
            f"<b>Nomi:</b> {mahsulot.nomi}\n"
            f"<b>Tavsif:</b> {mahsulot.tavsifi}\n\n"
            f"<b>Xususiyatlar:</b>\n{xususiyatlar}"
        )

        # Inline tugma: qayta tekshirish
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("🔄 Boshqa mahsulotlarni tekshirish", callback_data="retry")
        markup.add(btn)

        # Rasm bilan yuborish
        if asosiy_rasm and os.path.exists(asosiy_rasm.rasm.path):
            with open(asosiy_rasm.rasm.path, 'rb') as f:
                bot.send_photo(
                    message.chat.id,
                    photo=f,
                    caption=caption_text
                    
                )
        else:
            # Agar rasm yo'q bo'lsa, matn va tugma
            bot.send_message(
                message.chat.id,
                text=caption_text
                
            )

        # Mahsulot original yozuvi alohida xabar sifatida
        bot.send_message(
            message.chat.id,
            "✅ <b>Bu mahsulot original!</b>",
            reply_markup=markup
        )

    except TasdiqlovchiKod.DoesNotExist:
        logging.error(f"Code not found or already used: {code}")
        # Inline tugma yo'q, avtomatik ID so'raymiz
        if TasdiqlovchiKod.objects.filter(code=code).exists():
            # Kod mavjud, faqat ishlatilgan
            bot.send_message(
                message.chat.id,
                "❌ Bu mahsulot avval bot orqali tekshirilgan, agar siz tekshirmagan bo'lsangiz - bu mahsulot sohta"
            )
        else:
            # Kod bazada yo'q
            bot.send_message(
                message.chat.id,
                "❌ Bu mahsulot sohta yoki ID va codeni tog'ri ekanligiga ishonch hosil qiling!"
            )

        bot.send_message(
            message.chat.id,
            "🔎 Yana tekshirib ko'rishimiz mumkin, IDni kiriting:"
        )
            
        user_states[message.chat.id] = {"step": "id"}

    else:
        # Mahsulot topilganda, user_state ni tozalaymiz
        user_states.pop(message.chat.id, None)


# Retry callback
@bot.callback_query_handler(func=lambda call: call.data == "retry")
def retry(call):
    logging.info(f"Retry pressed by {call.from_user.id}")
    user_states[call.message.chat.id] = {"step": "id"}
    bot.send_message(call.message.chat.id, "ID ni qaytadan kiriting:")

# Admin /send command
@bot.message_handler(commands=['send'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        logging.warning(f"Unauthorized /send attempt by {message.from_user.id}")
        return

    if not message.reply_to_message:
        bot.send_message(message.chat.id, "Reply qilib yuboring.")
        return

    users = TelegramFoydalanuvchi.objects.all()
    success = 0

    for user in users:
        try:
            bot.copy_message(
                chat_id=user.telegram_id,
                from_chat_id=message.chat.id,
                message_id=message.reply_to_message.message_id
            )
            success += 1
        except Exception as e:
            logging.error(f"Failed to send to {user.telegram_id}: {str(e)}")
            continue

    bot.send_message(
        message.chat.id,
        f"✅ Yuborildi: {success} ta foydalanuvchiga"
    )

logging.info("Bot started polling...")
bot.infinity_polling(skip_pending=True)
