import discord
from discord.ext import commands
from data.db_setup import session

def setup(bot):
    @bot.event
    async def on_ready():
        await bot.change_presence(status=discord.Status.dnd,activity=discord.Activity(type=discord.ActivityType.watching, name="um filme"))
        print(f'Bot inicializado como {bot.user}')

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Comando não encontrado. Use db!help para ver a lista de comandos.")
        else:
            await ctx.send(f"Ocorreu um erro: {str(error)}")
    @bot.event
    async def on_disconnect():
        session.close()
