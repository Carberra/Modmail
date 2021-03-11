from pathlib import Path

import discord
from discord.ext import commands

import modmail
from modmail import Config


class Bot(commands.Bot):
    __slots__ = ("ready", "extensions")

    def __init__(self) -> None:
        self.ready = False
        self.extensions = [p.stem for p in Path(".").glob("./modmail/bot/extensions/*.py")]

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
        await self.change_presence(activity=discord.Activity(name="DM reports", type=discord.ActivityType.listening))
        self.ready = True
        print(f" Bot ready.")
