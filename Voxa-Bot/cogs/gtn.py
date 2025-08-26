from discord.ext import commands
import random

class GuessTheNumber(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_active = False
        self.secret = None
        self.channel_id = None 

    @commands.command()
    @commands.has_permissions(manage_guild=True)  
    async def gtn(self, ctx):
        
        if self.game_active:
            await ctx.send("A Guess the Number game is already running!")
            return

        self.secret = random.randint(1, 100)
        self.game_active = True
        self.channel_id = ctx.channel.id  # fixed name
        print("secret :",self.secret)

        await ctx.send(
            "**Guess The Number Event Started!**\n"
            "I’ve picked a number between **1 and 100**.\n"
            "Use `!guess <number>` to play!"
        )

    @commands.command()
    async def guess(self, ctx, number: int = None):
        """Make a guess if the event is active."""
        if not self.game_active:
            await ctx.send("There’s no active Guess The Number event right now!")
            return

        if ctx.channel.id != self.channel_id:
            await ctx.send("You can only guess in the event channel!")
            return

        if number is None:
            await ctx.send("Usage: `!guess <number>`")
            return

        if number == self.secret:
            await ctx.send(
                f"** {ctx.author.mention}** guessed it! The number was **{self.secret}**"
            )
        
            self.game_active = False
            self.secret = None
            self.channel_id = None
        else:
            await ctx.message.add_reaction("❌")  

async def setup(bot):
    await bot.add_cog(GuessTheNumber(bot))
