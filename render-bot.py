import requests
import random
import time
import json
import os

# TOKENNI BU YERGA QO'YING
MAIN_BOT_TOKEN = os.getenv("BOT_TOKEN", "8571970125:AAFrjrJeRabWiUiSSTdflpCvMPOM11Jae6E")

# SOZLAMALAR
BOT_ARMY = []
REACTIONS_PER_BOT = 3
DELAY_BETWEEN_REACTIONS = (1, 2)
BOT_FILE = "bot_army.json"

# REAKSIYALAR
ALL_REACTIONS = ["👍", "❤️", "🔥", "👏", "😁", "🎉", "💯", "⭐", "🤩", "😍", "👌", "💪"]

class TelegramBot:
    def __init__(self, token=None):
        self.token = token or MAIN_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.session = requests.Session()
        self.session.timeout = 10
    
    def get_me(self):
        """Bot ma'lumotlarini olish"""
        try:
            response = self.session.get(f"{self.base_url}/getMe")
            data = response.json()
            return data
        except Exception as e:
            print(f"❌ Bot ma'lumotlari olinmadi: {e}")
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
            return response.json()
        except Exception as e:
            print(f"❌ Xabar yuborilmadi: {e}")
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
            return data
        except Exception as e:
            print(f"❌ Reaksiya qo'yilmadi: {e}")
            return {"ok": False}
    
    def delete_webhook(self):
        """Webhook ni o'chirish"""
        try:
            response = self.session.get(f"{self.base_url}/deleteWebhook")
            return response.json()
        except:
            return {"ok": False}
    
    def get_updates(self, offset=None, timeout=30):
        """Yangilanishlarni olish"""
        try:
            params = {"timeout": timeout}
            if offset:
                params["offset"] = offset
            
            response = self.session.get(f"{self.base_url}/getUpdates", params=params)
            return response.json()
        except Exception as e:
            print(f"❌ Updates olinmadi: {e}")
            return {"ok": False, "result": []}

class BotArmySystem:
    def __init__(self):
        self.main_bot = TelegramBot(MAIN_BOT_TOKEN)
        self.offset = 0
        self.bot_army = []
        self.load_bot_army()
        
    def load_bot_army(self):
        """Bot army ni fayldan yuklash"""
        global BOT_ARMY
        try:
            if os.path.exists(BOT_FILE):
                with open(BOT_FILE, 'r') as f:
                    self.bot_army = json.load(f)
                    BOT_ARMY = self.bot_army.copy()
                print(f"✅ {len(self.bot_army)} ta army bot yuklandi")
            else:
                print("ℹ️ Army botlar fayli yo'q")
        except Exception as e:
            print(f"❌ Army botlar yuklanmadi: {e}")
            self.bot_army = []
    
    def save_bot_army(self):
        """Bot army ni faylga saqlash"""
        global BOT_ARMY
        try:
            with open(BOT_FILE, 'w') as f:
                json.dump(self.bot_army, f, indent=2)
            BOT_ARMY = self.bot_army.copy()
            print(f"✅ {len(self.bot_army)} ta army bot saqlandi")
        except Exception as e:
            print(f"❌ Army botlar saqlanmadi: {e}")
    
    def add_bot_to_army(self, token):
        """Army ga yangi bot qo'shish"""
        # Token formati tekshirish
        if not token or len(token) < 30:
            return False, "❌ Token noto'g'ri formatda"
        
        # Token allaqachon mavjudligini tekshirish
        if token in self.bot_army:
            return False, "❌ Bu bot allaqachon qo'shilgan"
        
        if token == MAIN_BOT_TOKEN:
            return False, "❌ Bu asosiy botning tokeni"
        
        # Botni tekshirish
        test_bot = TelegramBot(token)
        bot_info = test_bot.get_me()
        
        if bot_info.get("ok"):
            self.bot_army.append(token)
            self.save_bot_army()
            
            username = bot_info["result"].get("username", "Noma'lum")
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
                return True, f"✅ Bot o'chirildi! Qolgan: {len(self.bot_army)} ta"
            else:
                return False, "❌ Noto'g'ri raqam"
        except:
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
        
        message += f"\n🗑 <b>O'chirish:</b> /delete1, /delete2, ..."
        return message
    
    def process_post_reactions(self, chat_id, message_id):
        """Postga reaksiya qo'yish"""
        print(f"\n🎯 POSTGA REAKSIYALAR QO'YILMOQDA...")
        print(f"💬 Chat: {chat_id}")
        print(f"📝 Message: {message_id}")
        print("-" * 50)
        
        total_reactions = 0
        successful_reactions = 0
        
        # 1. Asosiy bot reaksiyalari
        print(f"\n👑 ASOSIY BOT:")
        reactions = random.sample(ALL_REACTIONS, min(REACTIONS_PER_BOT, len(ALL_REACTIONS)))
        
        for i, emoji in enumerate(reactions, 1):
            result = self.main_bot.send_reaction(chat_id, message_id, emoji)
            total_reactions += 1
            
            if result.get("ok"):
                successful_reactions += 1
                print(f"   {i}. ✅ {emoji}")
            else:
                print(f"   {i}. ❌ {emoji}")
                if "description" in result:
                    print(f"      Xato: {result['description']}")
            
            if i < len(reactions):
                time.sleep(random.uniform(*DELAY_BETWEEN_REACTIONS))
        
        # 2. Army botlar reaksiyalari
        if self.bot_army:
            print(f"\n🤖 ARMY BOTLAR ({len(self.bot_army)} ta):")
            
            for bot_index, token in enumerate(self.bot_army, 1):
                army_bot = TelegramBot(token)
                
                # Botni tekshirish
                bot_info = army_bot.get_me()
                if not bot_info.get("ok"):
                    print(f"   {bot_index}. ❌ Bot ishlamayapti")
                    continue
                
                bot_username = bot_info["result"].get("username", f"Bot_{bot_index}")
                print(f"   {bot_index}. 🤖 @{bot_username}")
                
                # Army bot reaksiyalari
                army_reactions = random.sample(ALL_REACTIONS, min(REACTIONS_PER_BOT, len(ALL_REACTIONS)))
                
                for i, emoji in enumerate(army_reactions, 1):
                    result = army_bot.send_reaction(chat_id, message_id, emoji)
                    total_reactions += 1
                    
                    if result.get("ok"):
                        successful_reactions += 1
                        print(f"      {i}. ✅ {emoji}")
                    else:
                        print(f"      {i}. ❌ {emoji}")
                    
                    if i < len(army_reactions):
                        time.sleep(random.uniform(*DELAY_BETWEEN_REACTIONS))
                
                # Botlar orasida kechikish
                if bot_index < len(self.bot_army):
                    time.sleep(random.uniform(0.5, 1))
        
        print("-" * 50)
        print(f"📊 NATIJA: {successful_reactions}/{total_reactions} ta reaksiya")
        print("=" * 50)
        
        return successful_reactions, total_reactions
    
    def handle_command(self, chat_id, command, user_name):
        """Foydalanuvchi komandalarini boshqarish"""
        
        if command == "/start":
            welcome_msg = f"""👋 Salom, {user_name}!

🤖 <b>BOT ARMY - Reaksiya Sistemasi</b>
⭐ Har qanday postga reaksiya qo'yadi: 
  • 📝 Matn
  • 🎵 Musiqa
  • 🎬 Video
  • 📷 Rasm
  • 📎 Fayllar

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
2. Kanalga HAR QANDAY post joylang
3. Botlar AVTOMATIK reaksiya qo'yadi!"""
            
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
            except:
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
🔄 Status: ✅ Faol

🎵 SUPPORTED MEDIA:
• Text messages
• Music/audio
• Videos
• Photos
• Documents
• Stickers"""
            
            self.main_bot.send_message(chat_id, stats_msg)
        
        elif command == "/help":
            help_msg = """📖 <b>YORDAM VA QO'LLANMA</b>

<b>BOT QANDAY ISHLAYDI?</b>
1. Bir nechta bot yaratasiz
2. Barcha botlarni kanalga ADMIN qilasiz
3. Har qanday post (matn, musiqa, video) joylaganingizda, barcha botlar reaksiya qo'yadi

<b>ASOSIY KOMANDALAR:</b>
• /start - Botni ishga tushirish
• /addbot - Yangi bot qo'shish
• /mybots - Botlar ro'yxati
• /stats - Statistika

<b>SUPPORTED POST TYPES:</b>
✅ Text messages
✅ Music and audio files
✅ Videos
✅ Photos
✅ Documents
✅ Stickers
✅ Voice messages
✅ Polls

<b>MUHIM ESHTUTISH:</b>
• Har bir botni kanalga ADMIN qiling!
• Tokenlarni hech kimga bermang!"""
            
            self.main_bot.send_message(chat_id, help_msg)
        
        elif command == "/test":
            test_msg = "✅ Bot ishlayapti! Kanalga HAR QANDAY post (matn, musiqa, video) qo'ying va reaksiyalarni tomosha qiling!"
            self.main_bot.send_message(chat_id, test_msg)
        
        elif command == "/media":
            media_msg = """🎵 <b>SUPPORTED MEDIA TYPES:</b>

Bot quyidagi post turlariga reaksiya qo'yadi:

<b>✅ SUPPORTED:</b>
• 📝 Text messages
• 🎵 Music & audio files
• 🎬 Videos
• 📷 Photos
• 📎 Documents
• 🎭 Stickers
• 🎤 Voice messages
• 📊 Polls
• 🎮 Games

<b>❌ NOT SUPPORTED:</b>
• Contact sharing
• Location sharing
• Video notes

<b>💡 TIP:</b>
Bot har qanday media postiga avtomatik reaksiya qo'yadi!"""
            self.main_bot.send_message(chat_id, media_msg)
        
        else:
            unknown_msg = f"""🤔 Noma'lum komanda: {command}

<b>Mavjud komandalar:</b>
/start - Botni boshlash
/addbot - Yangi bot qo'shish
/mybots - Botlar ro'yxati
/stats - Statistika
/media - Qo'llab-quvvatlanadigan media turlari
/help - Yordam"""
            
            self.main_bot.send_message(chat_id, unknown_msg)
    
    def start_polling(self):
        """Botni ishga tushirish"""
        print("=" * 60)
        print("🤖 TELEGRAM BOT ARMY v2.0 - All Media Support")
        print("🎵 Now supports: Text, Music, Video, Photos, Documents")
        print("=" * 60)
        
        # Botni tekshirish
        bot_info = self.main_bot.get_me()
        if not bot_info.get("ok"):
            print("❌ TOKEN XATO!")
            print("Iltimos, to'g'ri token kiriting yoki yangi bot yarating")
            return
        
        # Bot ma'lumotlari
        username = bot_info["result"]["username"]
        first_name = bot_info["result"]["first_name"]
        bot_id = bot_info["result"]["id"]
        
        print(f"✅ BOT MUVOFIQQIYATLI ULANDI!")
        print(f"🤖 Username: @{username}")
        print(f"📛 Ism: {first_name}")
        print(f"🆔 ID: {bot_id}")
        print(f"🔗 Link: https://t.me/{username}")
        print(f"👥 Army botlar: {len(self.bot_army)} ta")
        print("\n🎵 QO'LLAB-QUVVATLANADI:")
        print("  • 📝 Matn xabarlar")
        print("  • 🎵 Musiqa va audio")
        print("  • 🎬 Videolar")
        print("  • 📷 Rasmlar")
        print("  • 📎 Hujjatlar")
        print("=" * 60)
        
        # Webhook o'chirish
        self.main_bot.delete_webhook()
        print("✅ Webhook o'chirildi")
        
        print("\n🔄 Yangilanishlar kutilmoqda...")
        print("📱 Botga /start yuboring")
        print("📢 Kanalga HAR QANDAY post (matn/musiqa/video) qo'ying")
        print("=" * 60 + "\n")
        
        # Polling sikli
        while True:
            try:
                updates = self.main_bot.get_updates(offset=self.offset)
                
                if updates.get("ok") and updates.get("result"):
                    for update in updates["result"]:
                        self.offset = update["update_id"] + 1
                        
                        # Shaxsiy xabar
                        if "message" in update:
                            message = update["message"]
                            chat_id = message["chat"]["id"]
                            text = message.get("text", "").strip()
                            user_name = message["from"].get("first_name", "Foydalanuvchi")
                            
                            # Faqat xabar bor bo'lsa
                            if text:
                                print(f"📩 {user_name}: {text}")
                                self.handle_command(chat_id, text, user_name)
                        
                        # Kanal posti - HAR QANDAY POST TURI
                        elif "channel_post" in update:
                            post = update["channel_post"]
                            chat_id = post["chat"]["id"]
                            message_id = post["message_id"]
                            channel_name = post["chat"].get("title", "Kanal")
                            
                            # POST TURINI ANIQLASH
                            post_type = "📝 Matn"
                            
                            if "text" in post:
                                post_type = "📝 Matn"
                                text_preview = post["text"][:50] + "..." if len(post.get("text", "")) > 50 else post.get("text", "")
                                print(f"\n📢 YANGI POST: {channel_name} ({post_type})")
                                print(f"📝 Matn: {text_preview}")
                            
                            elif "audio" in post:
                                post_type = "🎵 Musiqa"
                                audio = post["audio"]
                                title = audio.get("title", "Noma'lum")
                                print(f"\n📢 YANGI POST: {channel_name} ({post_type})")
                                print(f"🎵 Musiqa: {title}")
                            
                            elif "video" in post:
                                post_type = "🎬 Video"
                                video = post["video"]
                                print(f"\n📢 YANGI POST: {channel_name} ({post_type})")
                                print(f"🎬 Video ID: {video.get('file_id')}")
                            
                            elif "photo" in post:
                                post_type = "📷 Rasm"
                                print(f"\n📢 YANGI POST: {channel_name} ({post_type})")
                                print(f"📷 Rasmlar: {len(post['photo'])} ta")
                            
                            elif "document" in post:
                                post_type = "📎 Hujjat"
                                doc = post["document"]
                                file_name = doc.get("file_name", "Noma'lum")
                                print(f"\n📢 YANGI POST: {channel_name} ({post_type})")
                                print(f"📎 Fayl: {file_name}")
                            
                            elif "voice" in post:
                                post_type = "🎤 Ovoz"
                                print(f"\n📢 YANGI POST: {channel_name} ({post_type})")
                            
                            elif "sticker" in post:
                                post_type = "🎭 Stiker"
                                sticker = post["sticker"]
                                emoji = sticker.get("emoji", "")
                                print(f"\n📢 YANGI POST: {channel_name} ({post_type})")
                                print(f"🎭 Stiker: {emoji}")
                            
                            else:
                                # Boshqa post turlari
                                post_type = "📌 Boshqa"
                                print(f"\n📢 YANGI POST: {channel_name} ({post_type})")
                                print(f"📝 Post ID: {message_id}")
                            
                            # HAR QANDAY POSTGA REAKSIYA QO'YISH
                            print(f"🆔 Post ID: {message_id}")
                            print(f"📊 Turi: {post_type}")
                            
                            # Reaksiyalarni qo'yish
                            self.process_post_reactions(chat_id, message_id)
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n\n⏹️ Bot to'xtatildi")
                print("👋 Xayr!")
                break
            
            except Exception as e:
                print(f"\n⚠️ Xatolik yuz berdi: {e}")
                print("🔄 5 soniya kutish...")
                time.sleep(5)

def main():
    """Dasturni ishga tushirish"""
    print("🎯 TELEGRAM BOT ARMY v2.0 - All Media Support")
    print("⚡ Har qanday postga reaksiya: matn, musiqa, video, rasm")
    print("🌐 Deployed on Railway")
    print("=" * 50)
    
    # Tizimni ishga tushirish
    system = BotArmySystem()
    system.start_polling()

if __name__ == "__main__":
    main()
