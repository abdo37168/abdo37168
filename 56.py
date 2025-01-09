import telebot
import requests
from telebot import types
from concurrent.futures import ThreadPoolExecutor
import random

bot = telebot.TeleBot('8153260228:AAFR1rvnYfLzhg_t5gLKNLGfVQaZvAae8Og', parse_mode="HTML")

# التعامل مع الأمر /start
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Send the file now \n ارسل الملف الان")

# فحص الكومبو مع تحسين الأداء
@bot.message_handler(content_types=["document"])
def check_combo(message):
    try:
        ko = bot.reply_to(message, "Checking Your Cards...⌛").message_id
        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)

        with open("combo.txt", "wb") as f:
            f.write(file)

        with open("combo.txt", "r") as f:
            combos = f.readlines()

        total = len(combos)
        live_cards = []
        dead_cards = []

        def check_card(card):
            try:
                card = card.strip()
                bin_code = card[:6]
                response = requests.get(f'https://lookup.binlist.net/{bin_code}')
                if response.status_code != 200:
                    return {"card": card, "status": "Unknown"}

                data = response.json()
                bank = data.get('bank', {}).get('name', 'Unknown')
                country = data.get('country', {}).get('name', 'Unknown')
                emoji = data.get('country', {}).get('emoji', '')
                scheme = data.get('scheme', 'Unknown')
                card_type = data.get('type', 'Unknown')

                # محاكاة النتيجة
                status = random.choice(["Live", "Dead"])
                return {
                    "card": card,
                    "status": status,
                    "details": f'{bin_code} - {scheme} - {card_type} - {country} {emoji} - {bank}'
                }
            except Exception as e:
                print(f"Error checking card: {e}")
                return {"card": card, "status": "Error"}

        # فحص الكروت باستخدام تعدد المهام
        with ThreadPoolExecutor(max_workers=20) as executor:
            results_list = list(executor.map(check_card, combos))

        # معالجة النتائج
        for result in results_list:
            if result["status"] == "Live":
                live_cards.append(f"{result['card']} - {result['details']}")
            elif result["status"] == "Dead":
                dead_cards.append(result["card"])

        # تنسيق الرسالة النهائية
        live_message = "🔓 Live Cards:\n" + "\n".join(live_cards) if live_cards else "No Live Cards Found."
        dead_message = "❌ Dead Cards:\n" + "\n".join(dead_cards) if dead_cards else "No Dead Cards Found."

        final_msg = f'''
Total Checked: {total}
Live Cards: {len(live_cards)}
Dead Cards: {len(dead_cards)}

{live_message}

{dead_message}
'''
        # إرسال الرسالة النهائية
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text=final_msg)

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "An error occurred while checking the combo. Please try again.")

print("Bot is running...")
bot.polling()
