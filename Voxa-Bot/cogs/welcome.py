import discord
from discord.ext import commands

class WelcomeGoodbye(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.text_channels, name="welcome")  
        if channel:
            embed = discord.Embed(
                title=f"Welcome {member.name}!",
                description="We are happy to have you here! 🎉",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.avatar.url)
            await channel.send(embed=embed)

          
            role = discord.utils.get(member.guild.roles, name="Member")
            if role:
                await member.add_roles(role)

    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = discord.utils.get(member.guild.text_channels, name="goodbye")  
        if channel:
            embed = discord.Embed(
                title=f"Goodbye {member.name}",
                description="We hope to see you again soon!",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=member.avatar.url)
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(WelcomeGoodbye(bot))
