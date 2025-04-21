import asyncio
import aiohttp
from keep_alive import keep_alive
from telethon import TelegramClient, events
import telethon.tl.types

# ===== Запуск мини-сервера для Railway =====
keep_alive()

# ===== Настройки Telegram API =====
api_id = 7132208
api_hash = 'badc02193dbca8114da052096884a792'

# ===== Каналы =====
# Используем именно ID канала
source_channel = -1001438042829  # ID канала-источника (без кавычек!)
my_channel = 'schemes_alley'  # Имя твоего канала БЕЗ https://t.me/

# ===== Настройки DeepSeek API =====
deepseek_api_url = 'https://api.deepseek.com/v1/chat/completions'
api_key = 'sk-39d991d8c2664a3881a6bef71c172299'

# ===== Инициализация клиента =====
client = TelegramClient('anon', api_id, api_hash)

async def process_text_with_deepseek(text):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    system_prompt = """Ты - профессиональный редактор и аналитик. 
    Твоя задача - проанализировать предоставленный текст и создать новое, 
    более структурированное и информативное сообщение для канала в телеграмме "Схемный Переулок". 
    Сделай так чтобы текст был понятен для людей, в дружественной форме, попунктам. Максимальное количество символов 500."""

    payload = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': text}
        ],
        'temperature': 0.7
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(deepseek_api_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('choices', [{}])[0].get('message', {}).get('content', 'Ошибка: пустой ответ от DeepSeek')
                else:
                    return f'Ошибка API: {response.status} - {await response.text()}'
        except Exception as e:
            return f'Ошибка при обращении к API: {str(e)}'

@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    try:
        if event.media:
            original_text = event.text or ""
            print(f'Получен новый пост с файлом. Текст: {original_text[:100]}...')

            processed_text = ""
            if original_text:
                processed_text = await process_text_with_deepseek(original_text)
                print(f'Текст обработан через DeepSeek: {processed_text[:100]}...')

            await client.send_file(
                my_channel,
                event.media,
                caption=processed_text if processed_text else None
            )
            print('Файл успешно отправлен в целевой канал')
        else:
            print('Пропущен пост без медиа.')
    except Exception as e:
        print(f'Ошибка при обработке сообщения: {str(e)}')

async def main():
    await client.start()
    print('Бот успешно запущен и ожидает новые сообщения...')
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
