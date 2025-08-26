import discord
from discord.ext import commands
import random
import asyncio

class Draw(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def draw(self, ctx):
        print("!draw command triggered")  

        
        members = [m for m in ctx.guild.members if not m.bot and m.id != ctx.author.id]
        if not members:
            await ctx.send("No members found (only bots or just you)!")
            return

        chosen = random.choice(members)
        print(f"Chosen member: {chosen}")  

        artist = ctx.author  

        try:
            await artist.send(f"Please draw **{chosen.display_name}** and send me the image here!")
            print("DM sent to artist!")  
        except discord.Forbidden:
            await ctx.send(f"{artist.mention}, I can't DM you! Please open your DMs.")
            return

       
        def check(msg):
            return (
                msg.author.id == artist.id
                and isinstance(msg.channel, discord.DMChannel)
                and len(msg.attachments) > 0
            )

        await ctx.send(f"Asking {artist.mention} to draw {chosen.mention}...")

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=300) 
            print("Image received in DM!") 
        except asyncio.TimeoutError:
            await ctx.send(f"{artist.mention} took too long to respond!")
            return

       
        image = msg.attachments[0]
        await ctx.send(
            f"Here is the drawing of {chosen.mention} by {artist.mention}:",
            file=await image.to_file()
        )
        print("Image sent to server!")  

async def setup(bot):
    await bot.add_cog(Draw(bot))
