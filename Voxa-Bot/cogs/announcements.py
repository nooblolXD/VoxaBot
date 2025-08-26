import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, time
import json
import os

SETTINGS_FILE = "announcement_settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"channel_id": None, "hour": 18, "minute": 0}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

class Announcements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = load_settings()
        self.announcement_time = time(
            hour=self.settings["hour"], 
            minute=self.settings["minute"]
        )
        self.channel_id = self.settings["channel_id"]
        self.daily_announcement.start()

    def cog_unload(self):
        self.daily_announcement.cancel()

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setannounce(self, ctx, channel: discord.TextChannel):
        """announcement channel"""
        self.channel_id = channel.id
        self.settings["channel_id"] = self.channel_id
        save_settings(self.settings)
        await ctx.send(f"Announcements will be sent in {channel.mention}")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setannouncetime(self, ctx, hour: int, minute: int):
        """set the time for the auto announcement (24h format)"""
        if not (0 <= hour < 24 and 0 <= minute < 60):
            await ctx.send("Please provide a valid time (0-23 hour, 0-59 minute).")
            return
        self.announcement_time = time(hour=hour, minute=minute)
        self.settings["hour"] = hour
        self.settings["minute"] = minute
        save_settings(self.settings)
        await ctx.send(f"Daily announcement time set to {hour:02d}:{minute:02d}")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def announce(self, ctx, *, message: str):
        """Send an instant announcement"""
        if self.channel_id is None:
            await ctx.send("Please set an announcement channel first using !setannounce")
            return
        channel = self.bot.get_channel(self.channel_id)
        embed = discord.Embed(
            title="📢 Announcement",
            description=message,
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        await channel.send(embed=embed)
        await ctx.send("Announcement sent!")

    @tasks.loop(minutes=1)
    async def daily_announcement(self):
        """Automatic announcement daily at the specified time"""
        if self.channel_id is None:
            return

        now = datetime.utcnow().time().replace(second=0, microsecond=0)
        if now.hour == self.announcement_time.hour and now.minute == self.announcement_time.minute:
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                embed = discord.Embed(
                    title="Daily Reminder",
                    description="Don't forget to check today's updates!",
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                await channel.send(embed=embed)
                await asyncio.sleep(60) 

    @daily_announcement.before_loop
    async def before_daily_announcement(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Announcements(bot))
