import asyncio
from Twitch.Chat import ChatBot
from Utils import read_ini_settings


if __name__ == '__main__':
    #asyncio.run(run())
    bot = ChatBot()
    asyncio.run(bot.run(read_ini_settings("Twitch/TwitchChatBotSettings.ini")))
