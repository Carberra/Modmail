import datetime as dt
import random
import typing as t

import discord
from discord.ext import commands

import modmail
from modmail import Config
from modmail.utils import chron, string


class Mail(commands.Cog):
    __slots__ = ("bot", "cooldown")

    def __init__(self, bot: modmail.bot.Bot) -> None:
        self.bot = bot
        self.cooldown: t.List[discord.Member] = []

    async def handle_modmail(self, message: discord.Message) -> None:
        if message.author in self.cooldown:
            retry = self.bot.scheduler.get_job(f"{message.author.id}").next_run_time - dt.datetime.now(dt.timezone.utc)
            return await message.channel.send(
                f"Sorry, you're on cooldown! You can send another message in {chron.long_delta(retry)}."
            )

        if not 50 <= len(message.content) <= 1000:
            return await message.channel.send("Your message should be between 50 and 1,000 characters long.")

        member = self.bot.guild.get_member(message.author.id)

        fields = [
            {"name": "Member", "value": f"{member.name} (ID: {member.id})", "inline": False},
            {"name": "Message", "value": message.content, "inline": False},
        ]

        if message.mentions:
            fields.append(
                {
                    "name": "Other Mentions",
                    "value": "\n".join((f"{m.name}: {m.id}") for m in message.mentions),
                    "inline": False,
                }
            )

        struc = {
            "title": "Modmail",
            "color": random.randint(0x0, 0xFFFFFF),
            "thumbnail": {"url": f"{member.avatar_url}"},
            "footer": {"text": f"ID: {message.id}"},
            "image": {"url": att[0].url if len(att := message.attachments) else None},
            "fields": fields,
        }

        embed = discord.Embed.from_dict(struc)

        await self.output.send(embed=embed)

        await message.channel.send(
            "Message sent. If needed, a moderator will DM you regarding this issue. You'll need to wait 1 hour before sending another modmail."
        )

        self.cooldown.append(message.author)
        self.bot.scheduler.add_job(
            lambda m: self.cooldown.remove(m),
            id=f"{message.author.id}",
            next_run_time=dt.datetime.utcnow() + dt.timedelta(seconds=3600),
            args=[message.author],
        )

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.output = self.bot.get_channel(Config.MODMAIL_ID)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not isinstance(message.channel, discord.DMChannel):
            return

        await self.handle_modmail(message)


def setup(bot: modmail.bot.Bot) -> None:
    bot.add_cog(Mail(bot))
