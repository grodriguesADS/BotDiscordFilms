from discord.ext import commands
from data.db_setup import session

def setup(bot):
    @bot.event
    async def on_ready():
        print(f'Bot inicializado como {bot.user}')

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Comando não encontrado. Use db!helpdb para ver a lista de comandos.")
        else:
            await ctx.send(f"Ocorreu um erro: {str(error)}")
    @bot.event
    async def on_disconnect():
        session.close()
