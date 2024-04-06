import os

# You Can Get API ID And API HASH From: https://core.telegram.org/api/obtaining_api_id

API_ID = int(os.getenv("API_ID", "YourAPI_ID"))

API_HASH = os.getenv("API_HASH", "YourAPI_Hash")

BOT_TOKEN = os.getenv("BOT_TOKEN", "YourBotToken") #Telegram BoT Token, You Can Create One From: @BotFather

ADMIN = int(os.getenv("ADMIN", "TheBotAdminAccountID")) #The ID of Account That Will Use The BoT

