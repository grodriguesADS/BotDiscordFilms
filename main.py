import discord
from discord.ext import commands
from config.config import DISCORD_TOKEN, BOT_PREFIX
from bot import commands as bot_commands, events


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)


bot_commands.setup(bot)
events.setup(bot)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
