from discord.ext import commands
import discord

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        ltcy = round(self.bot.latency * 1000)  
        await ctx.send(f" Responce Time : **{ltcy}ms**")

async def setup(bot):
    await bot.add_cog(Ping(bot))
