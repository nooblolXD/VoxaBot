import discord
from discord.ext import commands

class PermissionsControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

   
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("error occured")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("error occured")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("error occured")
        else:
            await ctx.send("error occurred")
            
            print(f"Error in command {ctx.command}: {error}")

async def setup(bot):
    await bot.add_cog(PermissionsControl(bot))
