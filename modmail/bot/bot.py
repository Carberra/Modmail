from pathlib import Path

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands
from pytz import utc

import modmail
from modmail import Config


class Bot(commands.Bot):
    __slots__ = ("extensions", "scheduler")

    def __init__(self) -> None:
        self.extensions = [p.stem for p in Path(".").glob("./modmail/bot/extensions/*.py")]
        self.scheduler = AsyncIOScheduler()
        self.scheduler.configure(timezone=utc)

        super().__init__(
            command_prefix=Config.PREFIX,
            status=discord.Status.online,
            intents=discord.Intents.all(),
        )

    def __call__(self) -> None:
        self.run()

    def setup(self) -> None:
        print("Running setup...")
        for ext in self.extensions:
            self.load_extension(f"modmail.bot.extensions.{ext}")
            print(f" `{ext}` extension loaded.")

    def run(self) -> None:
        self.setup()
        print("Running bot...")
        super().run(Config.TOKEN, reconnect=True)

    async def close(self) -> None:
        print("Shutting down...")
        if stdout := self.get_cog("Hub").stdout:
            await stdout.send(f"Modmail v{modmail.__version__} is shutting down.")
        await super().close()
        print(" Bot shut down.")

    async def on_connect(self) -> None:
        print(f" Bot connected. DWSP latency: {self.latency * 1000:,.0f} ms")

    async def on_disconnect(self) -> None:
        print(f" Bot disconnected.")

    async def on_ready(self) -> None:
        self.scheduler.start()
        print(f" Scheduler started ({len(self.scheduler.get_jobs())} jobs scheduled).")

        await self.change_presence(activity=discord.Activity(name="DM reports", type=discord.ActivityType.listening))
        print(f" Presence set.")

        self.guild = self.get_guild(Config.GUILD_ID)
        print(f" Bot ready.")

    async def on_message(self, message: discord.Message) -> None:
        if message.guild and message.guild.me in message.mentions:
            await message.delete()
            try:
                await message.author.send(
                    f"Hey {message.author.name}! This bot is only for discrete reporting in DMs, and thus has no server functionality."
                )
            except discord.Forbidden:
                await message.author.send(
                    f"Hey {message.author.name}! This bot is only for discrete reporting in DMs, and thus has no server functionality.",
                    delete_after=10,
                )

    async def process_commands(self, message) -> None:
        pass
