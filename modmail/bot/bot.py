import discord
from discord.ext import commands

import modmail
from modmail import Config


class Bot(commands.Bot):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(
            command_prefix=Config.PREFIX,
            status=discord.Status.online,
            intents=discord.Intents.all(),
        )

    def __call__(self) -> None:
        self.run()

    def run(self) -> None:
        print("Running bot...")
        super().run(Config.TOKEN, reconnect=True)

    async def close(self) -> None:
        print("Shutting down...")

        # await self.get_cog("Hub").stdout.send(f"Modmail v{modmail.__version__} is shutting down.")
        await super().close()
        print(" Bot shut down.")

    async def on_connect(self) -> None:
        print(f" Bot connected. DWSP latency: {self.latency * 1000:,.0f} ms")

    async def on_disconnect(self) -> None:
        print(f" Bot disconnected.")

    async def on_ready(self) -> None:
        # await self.get_cog("Hub").stdout.send(f"Modmail v{modmail.__version__} is online!")
        print(f" Bot ready.")

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not isinstance(message.channel, discord.DMChannel):
            return

        print(message.content)
