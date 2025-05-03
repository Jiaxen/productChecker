import telegram

class TelegramClient:

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    async def send_message(self, message):
        bot = telegram.Bot(self.token)
        async with bot:
            await bot.send_message(text=message, chat_id=self.chat_id)
