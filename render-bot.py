import os
import requests
import random
import time
import json
import logging

# Logger sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Tokenni environment dan olish
MAIN_BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not MAIN_BOT_TOKEN:
    logger.error("BOT_TOKEN muhit o'zgaruvchisi topilmadi!")
    exit(1)

# Qolgan sozlamalar
BOT_ARMY = []
REACTIONS_PER_BOT = 3
DELAY_BETWEEN_REACTIONS = (1, 2)
BOT_FILE = "bot_army.json"

ALL_REACTIONS = ["👍", "❤️", "🔥", "👏", "😁", "🎉", "💯", "⭐", "🤩", "😍", "👌", "💪"]

class TelegramBot:
    def __init__(self, token=None):
        self.token = token or MAIN_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.session = requests.Session()
        self.session.timeout = 10
        logger.info(f"Bot yaratildi: {self.token[:15]}...")
    
    def get_me(self):
        """Bot ma'lumotlarini olish"""
        try:
            response = self.session.get(f"{self.base_url}/getMe")
            data = response.json()
            logger.debug(f"getMe response: {data}")
            return data
        except Exception as e:
            logger.error(f"Bot ma'lumotlari olinmadi: {e}")
            return {"ok": False}
    
    def send_message(self, chat_id, text, parse_mode="HTML"):
        """Xabar yuborish"""
        try:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }
            response = self.session.post(f"{self.base_url}/sendMessage", json=payload)
            data = response.json()
            logger.debug(f"sendMessage response: {data}")
            return data
        except Exception as e:
            logger.error(f"Xabar yuborilmadi: {e}")
            return {"ok": False}
    
    def send_reaction(self, chat_id, message_id, emoji):
        """Reaksiya qo'yish"""
        try:
            payload = {
                "chat_id": str(chat_id),
                "message_id": message_id,
                "reaction": [{"type": "emoji", "emoji": emoji}]
            }
            response = self.session.post(f"{self.base_url}/setMessageReaction", json=payload)
            data = response.json()
            logger.debug(f"Reaction response: {data}")
            return data
        except Exception as e:
            logger.error(f"Reaksiya qo'yilmadi: {e}")
            return {"ok": False}
    
    def delete_webhook(self):
        """Webhook ni o'chirish"""
        try:
            response = self.session.get(f"{self.base_url}/deleteWebhook")
            return response.json()
        except Exception as e:
            logger.error(f"Webhook o'chirilmadi: {e}")
            return {"ok": False}
    
    def get_updates(self, offset=None, timeout=30):
        """Yangilanishlarni olish"""
        try:
            params = {"timeout": timeout}
            if offset:
                params["offset"] = offset
            
            response = self.session.get(f"{self.base_url}/getUpdates", params=params)
            data = response.json()
            logger.debug(f"Updates response count: {len(data.get('result', []))}")
            return data
        except Exception as e:
            logger.error(f"Updates olinmadi: {e}")
            return {"ok": False, "result": []}

class BotArmySystem:
    def __init__(self):
        self.main_bot = TelegramBot(MAIN_BOT_TOKEN)
        self.offset = 0
        self.bot_army = []
        self.load_bot_army()
        logger.info("BotArmySystem ishga tushirildi")
        
    def load_bot_army(self):
        """Bot army ni fayldan yuklash"""
        global BOT_ARMY
        try:
            if os.path.exists(BOT_FILE):
                with open(BOT_FILE, 'r') as f:
                    self.bot_army = json.load(f)
                    BOT_ARMY = self.bot_army.copy()
                logger.info(f"{len(self.bot_army)} ta army bot yuklandi")
            else:
                logger.info("Army botlar fayli yo'q, yangi fayl yaratiladi")
        except Exception as e:
            logger.error(f"Army botlar yuklanmadi: {e}")
            self.bot_army = []
    
    def save_bot_army(self):
        """Bot army ni faylga saqlash"""
        global BOT_ARMY
        try:
            with open(BOT_FILE, 'w') as f:
                json.dump(self.bot_army, f, indent=2)
            BOT_ARMY = self.bot_army.copy()
            logger.info(f"{len(self.bot_army)} ta army bot saqlandi")
        except Exception as e:
            logger.error(f"Army botlar saqlanmadi: {e}")
    
    def add_bot_to_army(self, token):
        """Army ga yangi bot qo'shish"""
        if not token or len(token) < 30:
            return False, "❌ Token noto'g'ri formatda"
        
        if token in self.bot_army:
            return False, "❌ Bu bot allaqachon qo'shilgan"
        
        if token == MAIN_BOT_TOKEN:
            return False, "❌ Bu asosiy botning tokeni"
        
        test_bot = TelegramBot(token)
        bot_info = test_bot.get_me()
        
        if bot_info.get("ok"):
            self.bot_army.append(token)
            self.save_bot_army()
            
            username = bot_info["result"].get("username", "Noma'lum")
            logger.info(f"Yangi bot qo'shildi: @{username}")
            return True, f"✅ @{username} qo'shildi! Army: {len(self.bot_army)} ta"
        else:
            return False, "❌ Token noto'g'ri yoki bot ishlamayapti"
    
    def remove_bot_from_army(self, index):
        """Army dan bot o'chirish"""
        try:
            index = int(index) - 1
            if 0 <= index < len(self.bot_army):
                removed_token = self.bot_army.pop(index)
                self.save_bot_army()
                logger.info(f"Bot o'chirildi: index {index}")
                return True, f"✅ Bot o'chirildi! Qolgan: {len(self.bot_army)} ta"
            else:
                return False, "❌ Noto'g'ri raqam"
        except Exception as e:
            logger.error(f"Bot o'chirishda xatolik: {e}")
            return False, "❌ Xatolik yuz berdi"
    
    def show_bot_list(self):
        """Botlar ro'yxatini ko'rsatish"""
        if not self.bot_army:
            return "📋 Army botlar ro'yxati bo'sh\n\n🤖 /addbot - Yangi bot qo'shish"
        
        message = f"📋 <b>Army Botlar ({len(self.bot_army)} ta):</b>\n\n"
        
        for i, token in enumerate(self.bot_army, 1):
            bot = TelegramBot(token)
            info = bot.get_me()
            
            if info.get("ok"):
                username = info["result"].get("username", "Noma'lum")
                message += f"{i}. @{username}\n"
            else:
                message += f"{i}. ❌ Noto'g'ri token\n"
        
        message += f"\n🗑 <b>O'chirish:</b> /del1, /del2, ..."
        return message
    
    def process_post_reactions(self, chat_id, message_id):
        """Postga reaksiya qo'yish"""
        logger.info(f"Postga reaksiya qo'yish: chat_id={chat_id}, message_id={message_id}")
        
        total_reactions = 0
        successful_reactions = 0
        
        # Asosiy bot reaksiyalari
        logger.info("Asosiy bot reaksiyalarini qo'yish")
        reactions = random.sample(ALL_REACTIONS, min(REACTIONS_PER_BOT, len(ALL_REACTIONS)))
        
        for i, emoji in enumerate(reactions, 1):
            result = self.main_bot.send_reaction(chat_id, message_id, emoji)
            total_reactions += 1
            
            if result.get("ok"):
                successful_reactions += 1
                logger.info(f"Asosiy bot: ✅ {emoji}")
            else:
                logger.warning(f"Asosiy bot: ❌ {emoji}")
                if "description" in result:
                    logger.error(f"Xato: {result['description']}")
            
            if i < len(reactions):
                time.sleep(random.uniform(*DELAY_BETWEEN_REACTIONS))
        
        # Army botlar reaksiyalari
        if self.bot_army:
            logger.info(f"Army botlar reaksiyalarini qo'yish ({len(self.bot_army)} ta)")
            
            for bot_index, token in enumerate(self.bot_army, 1):
                army_bot = TelegramBot(token)
                
                bot_info = army_bot.get_me()
                if not bot_info.get("ok"):
                    logger.warning(f"Bot {bot_index} ishlamayapti")
                    continue
                
                bot_username = bot_info["result"].get("username", f"Bot_{bot_index}")
                logger.info(f"Army bot {bot_index}: @{bot_username}")
                
                army_reactions = random.sample(ALL_REACTIONS, min(REACTIONS_PER_BOT, len(ALL_REACTIONS)))
                
                for i, emoji in enumerate(army_reactions, 1):
                    result = army_bot.send_reaction(chat_id, message_id, emoji)
                    total_reactions += 1
                    
                    if result.get("ok"):
                        successful_reactions += 1
                        logger.info(f"  @{bot_username}: ✅ {emoji}")
                    else:
                        logger.warning(f"  @{bot_username}: ❌ {emoji}")
                    
                    if i < len(army_reactions):
                        time.sleep(random.uniform(*DELAY_BETWEEN_REACTIONS))
                
                if bot_index < len(self.bot_army):
                    time.sleep(random.uniform(0.5, 1))
        
        logger.info(f"Reaksiya natijasi: {successful_reactions}/{total_reactions}")
        return successful_reactions, total_reactions
    
    def handle_command(self, chat_id, command, user_name):
        """Foydalanuvchi komandalarini boshqarish"""
        logger.info(f"Command handled: {command} from {user_name}")
        
        if command == "/start":
            welcome_msg = f"""👋 Salom, {user_name}!

🤖 <b>BOT ARMY - Reaksiya Sistemasi</b>
⭐ Har bir postga ko'plab reaksiyalar!

<b>📋 ASOSIY KOMANDALAR:</b>
• /addbot - Yangi bot qo'shish
• /mybots - Botlar ro'yxati
• /removebot - Bot o'chirish
• /stats - Statistika
• /help - Yordam

<b>⚙️ JORIY SOZLAMALAR:</b>
• Army botlar: {len(self.bot_army)} ta
• Har bir bot: {REACTIONS_PER_BOT} ta reaksiya
• Jami reaksiya/post: {(len(self.bot_army) + 1) * REACTIONS_PER_BOT} ta

<b>🚀 BOSHLASH UCHUN:</b>
1. Botlarni kanalga ADMIN qiling
2. Kanalga post joylang
3. Botlar avtomatik reaksiya qo'yadi!"""
            
            self.main_bot.send_message(chat_id, welcome_msg)
        
        elif command == "/mybots" or command == "/listbots":
            bot_list = self.show_bot_list()
            self.main_bot.send_message(chat_id, bot_list)
        
        elif command == "/addbot":
            add_msg = """🤖 <b>YANGI BOT QO'SHISH</b>

<b>QADAMLAR:</b>
1️⃣ @BotFather ga o'ting
2️⃣ /newbot - yangi bot yarating
3️⃣ Bot nomi va username tanlang
4️⃣ TOKEN oling
5️⃣ Menga tokenni yuboring:

<code>/add 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz</code>

<b>⚠️ ESHTUTIB QO'YING:</b>
• Har bir yangi botni KANALGA ADMIN qiling!
• Barcha huquqlarni bering!"""
            
            self.main_bot.send_message(chat_id, add_msg)
        
        elif command.startswith("/add "):
            token = command.replace("/add ", "").strip()
            success, message = self.add_bot_to_army(token)
            self.main_bot.send_message(chat_id, message)
        
        elif command == "/removebot":
            if not self.bot_army:
                self.main_bot.send_message(chat_id, "❌ Army botlar yo'q!")
            else:
                remove_msg = f"""🗑 <b>BOT O'CHIRISH</b>

Qaysi botni o'chirmoqchisiz?

{self.show_bot_list()}

<b>O'chirish:</b> /del1, /del2, ..."""
                self.main_bot.send_message(chat_id, remove_msg)
        
        elif command.startswith("/del"):
            try:
                index = command.replace("/del", "")
                success, message = self.remove_bot_from_army(index)
                self.main_bot.send_message(chat_id, message)
            except Exception as e:
                logger.error(f"Bot o'chirishda xatolik: {e}")
                self.main_bot.send_message(chat_id, "❌ Xato! Raqam kiriting")
        
        elif command == "/stats":
            stats_msg = f"""📊 <b>STATISTIKA</b>

👑 Asosiy bot: 1 ta
🤖 Army botlar: {len(self.bot_army)} ta
📈 Jami botlar: {len(self.bot_army) + 1} ta

🎯 REAKSIYALAR:
• Har bir bot: {REACTIONS_PER_BOT} ta
• Jami/post: {(len(self.bot_army) + 1) * REACTIONS_PER_BOT} ta
• Mavjud reaksiyalar: {len(ALL_REACTIONS)} tur

📅 Bot yaratilgan: Bugun
🔄 Status: ✅ Faol"""
            
            self.main_bot.send_message(chat_id, stats_msg)
        
        elif command == "/help":
            help_msg = """📖 <b>YORDAM VA QO'LLANMA</b>

<b>BOT QANDAY ISHLAYDI?</b>
1. Bir nechta bot yaratasiz
2. Barcha botlarni kanalga ADMIN qilasiz
3. Post joylaganingizda, barcha botlar reaksiya qo'yadi

<b>ASOSIY KOMANDALAR:</b>
• /start - Botni ishga tushirish
• /addbot - Yangi bot qo'shish
• /mybots - Botlar ro'yxati
• /stats - Statistika

<b>MUHIM ESHTUTISH:</b>
• Har bir botni kanalga ADMIN qiling!
• Tokenlarni hech kimga bermang!"""
            
            self.main_bot.send_message(chat_id, help_msg)
        
        elif command == "/test":
            test_msg = "✅ Bot ishlayapti! Kanalga post qo'ying va reaksiyalarni tomosha qiling!"
            self.main_bot.send_message(chat_id, test_msg)
        
        elif command == "/status":
            status_msg = f"""🟢 Bot ishlayapti

📍 Host: Render.com
🕒 Server vaqti: {time.ctime()}
🤖 Army botlar: {len(self.bot_army)} ta
🖥️ Protsessor: Python {os.sys.version}
💾 Foydalanilgan fayl: {BOT_FILE}"""
            self.main_bot.send_message(chat_id, status_msg)
        
        else:
            unknown_msg = f"""🤔 Noma'lum komanda: {command}

<b>Mavjud komandalar:</b>
/start - Botni boshlash
/addbot - Yangi bot qo'shish
/mybots - Botlar ro'yxati
/stats - Statistika
/status - Bot holati
/help - Yordam"""
            
            self.main_bot.send_message(chat_id, unknown_msg)
    
    def start_polling(self):
        """Botni ishga tushirish"""
        logger.info("BotArmySystem polling ishga tushirilmoqda...")
        
        bot_info = self.main_bot.get_me()
        if not bot_info.get("ok"):
            logger.error("TOKEN XATO! Bot ishlamayapti")
            return
        
        username = bot_info["result"]["username"]
        first_name = bot_info["result"]["first_name"]
        
        logger.info(f"✅ BOT ULANDI: @{username} ({first_name})")
        logger.info(f"🤖 Army botlar: {len(self.bot_army)} ta")
        
        self.main_bot.delete_webhook()
        logger.info("Webhook o'chirildi")
        
        logger.info("Yangilanishlar kutilmoqda...")
        
        while True:
            try:
                updates = self.main_bot.get_updates(offset=self.offset)
                
                if updates.get("ok") and updates.get("result"):
                    for update in updates["result"]:
                        self.offset = update["update_id"] + 1
                        
                        if "message" in update:
                            message = update["message"]
                            chat_id = message["chat"]["id"]
                            text = message.get("text", "").strip()
                            user_name = message["from"].get("first_name", "Foydalanuvchi")
                            
                            if text:
                                logger.info(f"Xabar: {user_name}: {text}")
                                self.handle_command(chat_id, text, user_name)
                        
                        elif "channel_post" in update:
                            post = update["channel_post"]
                            
                            if "text" in post or "caption" in post:
                                chat_id = post["chat"]["id"]
                                message_id = post["message_id"]
                                channel_name = post["chat"].get("title", "Kanal")
                                
                                logger.info(f"Yangi post: {channel_name} (ID: {message_id})")
                                self.process_post_reactions(chat_id, message_id)
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Bot to'xtatildi")
                break
            
            except Exception as e:
                logger.error(f"Xatolik yuz berdi: {e}")
                time.sleep(5)

def main():
    """Dasturni ishga tushirish"""
    print("=" * 50)
    print("🎯 TELEGRAM BOT ARMY v2.0 - Render Edition")
    print("⚡ Ko'p Reaksiya Sistemasi")
    print("=" * 50)
    
    # Tizimni ishga tushirish
    system = BotArmySystem()
    system.start_polling()

if __name__ == "__main__":
    main()
