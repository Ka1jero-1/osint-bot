import telebot
import requests
from flask import Flask
from threading import Thread
import time

# --- НАСТРОЙКИ ---
TOKEN = 'ТВОЙ_ТОКЕН_ОТ_BOTFATHER'
bot = telebot.TeleBot(TOKEN)

# --- СЛОВАРЬ ПЛАТФОРМ (URL для проверки) ---
# Здесь мы проверяем никнеймы на популярных площадках
PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "Instagram": "https://www.instagram.com/{}/",
    "Steam": "https://steamcommunity.com/id/{}",
    "Roblox": "https://www.roblox.com/users/profile?username={}",
    "Pinterest": "https://www.pinterest.com/{}/",
    "Reddit": "https://www.reddit.com/user/{}",
    "Twitch": "https://www.twitch.tv/{}",
    "Twitter/X": "https://twitter.com/{}",
    "YouTube": "https://www.youtube.com/@{}",
    "VK": "https://vk.com/{}",
    "Facebook": "https://www.facebook.com/{}",
    "Flickr": "https://www.flickr.com/people/{}",
    "SoundCloud": "https://soundcloud.com/{}"
}

# Заголовки, чтобы сайты думали, что мы обычный браузер, а не бот
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "OSINT bot is working!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- ЛОГИКА БОТА ---
@bot.message_handler(commands=['start'])
def start_message(message):
    text = (
        "🕵️‍♂️ **Привет, хакер.**\n\n"
        "Кинь мне любой никнейм (без @), и я пробью его по открытым базам соцсетей. "
        "Я найду его профили, страницы и цифровой след за пару секунд.\n\n"
        "⚠️ *Я не взламываю пароли и не сливаю приватные базы. Я просто делаю то, что делает твой дружок-доксер, только в 100 раз быстрее.*"
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(content_types=['text'])
def search_username(message):
    # Очищаем ник от лишних символов
    username = message.text.strip().replace("@", "")
    
    if len(username) < 3:
        bot.reply_to(message, "❌ Ник слишком короткий, пидор. Введи нормальный.")
        return
        
    msg = bot.reply_to(message, f"⏳ Сканирую просторы интернета на наличие ника `{username}`... Жди.")
    
    found_profiles = []
    
    # Проходимся по каждому сайту
    for site_name, url_template in PLATFORMS.items():
        url = url_template.format(username)
        try:
            # Делаем запрос. Если сайт отвечает 200 (ОК) - значит профиль существует
            response = requests.get(url, headers=HEADERS, timeout=5)
            
            # Некоторые сайты возвращают 200 даже если профиля нет (редирект на главную)
            # Проверяем базовые коды ответа
            if response.status_code == 200:
                # Если в ответе нет фраз "not found" или "page not found"
                if "not found" not in response.text.lower() and "page not found" not in response.text.lower():
                    found_profiles.append(f"✅ [{site_name}]({url})")
        except requests.exceptions.RequestException:
            # Если сайт тупит или заблокировал запрос - просто пропускаем
            pass
            
    if found_profiles:
        result_text = f"🎯 **РЕЗУЛЬТАТЫ ПОИСКА ПО НИКУ `{username}`:**\n\n" + "\n".join(found_profiles)
        result_text += "\n\n*Скажи своему доксеру, чтобы сосал, пока я работаю.* 😎"
        bot.edit_message_text(result_text, message.chat.id, msg.message_id, parse_mode='Markdown', disable_web_page_preview=True)
    else:
        bot.edit_message_text(f"❌ По нику `{username}` я ничего не нашел. Либо человек-призрак, либо ты ввел хуйню.", message.chat.id, msg.message_id, parse_mode='Markdown')

# --- ЗАПУСК ---
if __name__ == "__main__":
    keep_alive()
    print("Бот-OSINT запущен!")
    bot.polling(none_stop=True)
