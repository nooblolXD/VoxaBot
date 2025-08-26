from discord.ext import commands
import random

class MathGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_active = False
        self.answer = None
        self.channel_id = None

    @commands.command()
    @commands.has_permissions(manage_guild=True)  
    async def math(self, ctx):
        if self.game_active:
            await ctx.send("A math game is already running!")
            return

        num1 = random.randint(1, 20)
        num2 = random.randint(1, 20)
        opr = random.choice(["+", "-", "*"])
        
        if opr == "+":
            self.answer = num1 + num2
        elif opr == "-":
            self.answer = num1 - num2
        else:
            self.answer = num1 * num2

        self.game_active = True
        self.channel_id = ctx.channel.id

        print("answer is :",self.answer)

        await ctx.send(
            f"**Math Challenge Started!**\n"
            f"Solve: **{num1} {opr} {num2}**\n"
            "Use `!answer <number>` to respond!\n"
            "First to answer wins!"
        )
    
    @commands.command()
    async def answer(self, ctx, guess: int = None):
        if not self.game_active:
            await ctx.send("There’s no active math game right now!")
            return
        
        if guess is None:
            await ctx.send("Usage: `!answer <number>`")
            return

        if guess == self.answer:
            await ctx.send(f"{ctx.author.mention} got it right! The answer was **{self.answer}**")
            
            
            self.game_active = False
            self.answer = None
            self.channel_id = None
        else:
            await ctx.message.add_reaction("❌")

async def setup(bot):
    await bot.add_cog(MathGame(bot))
