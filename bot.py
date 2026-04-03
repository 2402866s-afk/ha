# AIzaSyDsaRCFwQBvCiqCzE6DolbeaAr2hWhJ1j8
import asyncio
import requests
import re
import aiohttp   # ❗ shu qatorda bo‘lishi kerak
import html

from telethon import TelegramClient, events


# ================= SOZLAMALAR =================
API_ID = 
API_HASH = ""


GEMINI_KEY = ""


BOT_TOKEN = ""
TARGET_GROUP =  
SOURCE_GROUPS = ['@VODIY_TAKSI_XIZMATI' , -1001444235304  ,
                 '@toshkent_andijon_taksistlari',
                 '@Andijon_Toshkent_moshina',
                 '@Andijon_Samarqand_taksivodiyvoxa',
                 '@Toshkent_Fargona_Vodiy_Taksi',
                 '@Fargona_toshkent_fargonaN1',
                 
                 
                 ]

client = TelegramClient('shahriyor_fixer_final', API_ID, API_HASH)

# === 2. FILTRLAR (Maksimal kuchli) ===

# Haydovchi belgilari (Faqat o'zak so'zlar)
DRIVER_SIGNALS = [
    'cobalt', 'gentra', 'jentra', 'lacetti', 'lasetti', 'nexia', 'matiz', 'spark', 'damas',
    'кобальт', 'джентра', 'жентра', 'ласетти', 'нексия', 'матиз', 'спарк', 'дамас',
    'olaman', 'оламан', 'olamiz', 'оламиз', 'kammiz', 'каммиз', 'kamdamiz', 'камдамиз',
    'joy bor', 'жой бор', 'bo\'sh joy', 'бўш жой', 'bagaj', 'багаж', 'propan', 'пропан', 
    'metan', 'метан', 'benzin', 'бензин', 'klent', 'клент', 'klient', 'клиент', 
    'xizmati', 'хизмати', 'shafyor', 'шафёр', 'haydovchi', 'ҳайдовчи'
]

DESTINATIONS = ['toshkent', 'тошкент', 'andijon', 'андижон', 'namangan', 'наманган', 'fargona', 'qoqon']
CUSTOMER_KEYWORDS = ['bormi', 'kerak', 'ketishim', 'odam', 'pochta', 'yuk', 'moshin', 'taksi']

@client.on(events.NewMessage(chats=SOURCE_GROUPS))
async def handler(event):
    original_text = getattr(event.message, 'message', None) or getattr(event.message, 'text', '')
    if not original_text: return

    # Matnni tozalash
    text_clean = re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', original_text.lower())

    # Haydovchi filtrini tekshirish
    is_asking = any(q in text_clean for q in ['bormi', 'kerak', 'kere', 'nech', 'qancha'])
    if not is_asking:
        for signal in DRIVER_SIGNALS:
            if signal in text_clean:
                return

    # Shahar va mijoz kalit so'zlarini tekshirish
    has_dest = any(d in text_clean for d in DESTINATIONS)
    has_customer = any(c in text_clean for c in CUSTOMER_KEYWORDS) or re.search(r'\d{7,}', text_clean)

    if has_dest and has_customer:
        try:
            # Sender ma'lumotlarini olish
            sender = await event.get_sender()
            user_id = getattr(sender, 'id', None)
            first_name = html.escape(getattr(sender, 'first_name', "Mijoz"))
            safe_text = html.escape(original_text)

            # Link yaratish
            if sender and getattr(sender, 'username', None):
                link = f"https://t.me/{sender.username}"
            else:
                link = f"tg://user?id={user_id}"

            # GURUH LINKI (Agar link ishlamasa haydovchi guruhga o'tib yozishi uchun)
            chat = await event.get_chat()
            group_msg_link = ""
            if hasattr(chat, 'username') and chat.username:
                group_msg_link = f"https://t.me/{chat.username}/{event.message.id}"
            elif chat.id:
                # Maxfiy guruhlar uchun link formati
                clean_chat_id = str(chat.id).replace("-100", "")
                group_msg_link = f"https://t.me/c/{clean_chat_id}/{event.message.id}"

            post_text = (
                f"🎯 <b>YANGI MIJOZ TOPILDI!</b>\n\n"
                f"📝 <b>Xabar:</b> {safe_text}\n\n"
                f"👤 <b>Ismi:</b> {first_name}\n"
                f"🆔 <b>User ID:</b> <code>{user_id}</code>\n\n"
                f"🔗 <a href='{link}'><b>LICHKAGA YOZISH</b></a>\n"
                f"📍 <a href='{group_msg_link}'><b>GURUHDA JAVOB BERISH (100%)</b></a>\n\n"
                f"⚠️ <i>Lichka linki ishlamasa, 'Guruhda javob berish' tugmasini bosing!</i>"
            )

            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TARGET_GROUP, 
                "text": post_text, 
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }

            requests.post(url, json=payload)
            print(f"✅ Yuborildi: {user_id}")

        except Exception as e:
            print(f"❌ Xato: {e}")

async def main():
    await client.start()
    print("🚀 Bot ishga tushdi: Endi lichka yopiq bo'lsa ham guruh orqali bog'lanish mumkin!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
