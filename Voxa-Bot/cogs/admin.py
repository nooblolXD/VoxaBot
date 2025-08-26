import discord
from discord.ext import commands
import json
import os
import asyncio

# SETTINGS
BAN_APPEAL_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSeV8iAHa1FQCh5zK2wW1H5fOTrfizK5y_QEd5Hi-lGrvEPA9w/viewform?usp=dialog"
MOD_LOG_CHANNEL = "mod-log"         
REV_ROLE_NAME = "Wake up"
AUTO_ROLE_NAME = "Member"
WORD_FILE = "banned_words.json"     

# JSON WORD HELPERS
def load_words():
    if not os.path.exists(WORD_FILE):
        with open(WORD_FILE, "w") as f:
            json.dump([], f)
    with open(WORD_FILE, "r") as f:
        return json.load(f)

def save_words(words):
    with open(WORD_FILE, "w") as f:
        json.dump(words, f, indent=4)

# COG
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.banned_words = load_words()

    # LOG HELPER
    async def send_log(self, ctx, title, fields):
        log_channel = discord.utils.get(ctx.guild.text_channels, name=MOD_LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(title=title, color=discord.Color.blurple())
            for name, value in fields.items():
                embed.add_field(name=name, value=value, inline=False)
            await log_channel.send(embed=embed)

    # BAN
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if member == ctx.author:
            await ctx.send("You cannot ban yourself")
            return
        try:
            # DM first
            try:
                await member.send(
                    f"You have been permanently banned from {ctx.guild.name}.\n"
                    f"Reason: **{reason or 'No reason provided'}**\n"
                    f"Appeal here: {BAN_APPEAL_LINK}"
                )
            except:
                await ctx.send(f"Could not send DM to {member}.")

            
            await asyncio.sleep(3)

            
            await member.ban(reason=reason)
            await ctx.send(f"{member} has been permanently banned. Reason: {reason or 'No reason provided'}")

            await self.send_log(ctx, "User Banned", {
                "User": f"{member} ({member.id})",
                "Moderator": f"{ctx.author} ({ctx.author.id})",
                "Reason": reason or "No reason provided"
            })
        except Exception as e:
            await ctx.send(f"Failed to ban {member}: {e}")

    # UNBAN
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: str):
        try:
            if user.startswith("<@") and user.endswith(">"):
                user_id = int(user.replace("<@", "").replace("!", "").replace(">", ""))
            else:
                user_id = int(user)
            user_obj = await self.bot.fetch_user(user_id)
            found = False
            async for ban_entry in ctx.guild.bans():
                if ban_entry.user.id == user_obj.id:
                    await ctx.guild.unban(user_obj)
                    await ctx.send(f"{user_obj} has been unbanned.")
                    found = True
                    await self.send_log(ctx, "User Unbanned", {
                        "User": f"{user_obj} ({user_obj.id})",
                        "Moderator": f"{ctx.author} ({ctx.author.id})"
                    })
                    break
            if not found:
                await ctx.send(f"User {user_obj} is not in the ban list.")
        except ValueError:
            await ctx.send("Invalid ID or mention format.")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    # MUTE
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False)
        await member.add_roles(muted_role, reason=reason)
        await ctx.send(f"{member} has been muted. Reason: {reason or 'No reason provided'}")
        await self.send_log(ctx, "User Muted", {
            "User": f"{member} ({member.id})",
            "Moderator": f"{ctx.author} ({ctx.author.id})",
            "Reason": reason or "No reason provided"
        })

    # UNMUTE
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(f"{member} has been unmuted.")
            await self.send_log(ctx, "User Unmuted", {
                "User": f"{member} ({member.id})",
                "Moderator": f"{ctx.author} ({ctx.author.id})"
            })
        else:
            await ctx.send(f"{member} is not muted.")

    # REV
    @commands.command()
    @commands.has_permissions(mention_everyone=True)
    async def rev(self, ctx, *, message=None):
        role = discord.utils.get(ctx.guild.roles, name=REV_ROLE_NAME)
        if not role:
            await ctx.send(f"Role '{REV_ROLE_NAME}' not found.")
            return
        content = f"{role.mention} {message}" if message else f"{role.mention}"
        await ctx.send(content)

    # ADD ROLE
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, *, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"Role '{role_name}' not found.")
            return
        await member.add_roles(role)
        await ctx.send(f"Added role '{role_name}' to {member}.")
        await self.send_log(ctx, "Role Added", {
            "User": f"{member} ({member.id})",
            "Moderator": f"{ctx.author} ({ctx.author.id})",
            "Role": role_name
        })

    # REMOVE ROLE
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, *, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"Role '{role_name}' not found.")
            return
        await member.remove_roles(role)
        await ctx.send(f"Removed role '{role_name}' from {member}.")
        await self.send_log(ctx, "Role Removed", {
            "User": f"{member} ({member.id})",
            "Moderator": f"{ctx.author} ({ctx.author.id})",
            "Role": role_name
        })

    # AUTO-ASSIGN ROLE 
    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, name=AUTO_ROLE_NAME)
        if role:
            await member.add_roles(role)

    # WORD FILTER
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        for word in self.banned_words:
            if word.lower() in message.content.lower():
                try:
                    await message.delete()
                    warning_msg = await message.channel.send(
                        f"{message.author.mention}, your message contained a banned word and was deleted."
                    )
                    await warning_msg.delete(delay=5)
                    log_channel = discord.utils.get(message.guild.text_channels, name=MOD_LOG_CHANNEL)
                    if log_channel:
                        embed = discord.Embed(title="Banned Word Detected", color=discord.Color.red())
                        embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=False)
                        embed.add_field(name="Message", value=message.content, inline=False)
                        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
                        await log_channel.send(embed=embed)
                except Exception as e:
                    print(f"Failed to delete message: {e}")
                break

    # ADD WORD
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def addword(self, ctx, *, word):
        word = word.lower()
        if word in self.banned_words:
            await ctx.send(f"'{word}' is already in the banned words list.")
            return
        self.banned_words.append(word)
        save_words(self.banned_words)
        await ctx.send(f"Added '{word}' to banned words list.")

    # REMOVE WORD
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def removeword(self, ctx, *, word):
        word = word.lower()
        if word not in self.banned_words:
            await ctx.send(f"'{word}' is not in the banned words list.")
            return
        self.banned_words.remove(word)
        save_words(self.banned_words)
        await ctx.send(f"Removed '{word}' from banned words list.")

    # LIST WORDS
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def listwords(self, ctx):
        if not self.banned_words:
            await ctx.send("No banned words set.")
            return
        await ctx.send("Banned words:\n" + ", ".join(self.banned_words))

# COG SETUP
async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))






    #ERROR HANDLER 
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{ctx.author.mention}, you don't have permission to use this command.")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{ctx.author.mention}, missing arguments. Use `!help {ctx.command}` for details.")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"{ctx.author.mention}, invalid argument format.")
            return
        if isinstance(error, commands.CommandNotFound):
            return  

        
        await ctx.send(f"An unexpected error occurred while running `{ctx.command}`.")
        try:
            log_channel = discord.utils.get(ctx.guild.text_channels, name=MOD_LOG_CHANNEL)
            if log_channel:
                embed = discord.Embed(title="Command Error", color=discord.Color.red())
                embed.add_field(name="User", value=f"{ctx.author} ({ctx.author.id})", inline=False)
                embed.add_field(name="Command", value=ctx.message.content, inline=False)
                embed.add_field(name="Error", value=str(error), inline=False)
                await log_channel.send(embed=embed)
        except:
            pass

