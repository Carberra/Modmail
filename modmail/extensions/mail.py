# Copyright (c) 2020-2021, Carberra Tutorials
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import asyncio
import datetime as dt
import typing as t

import hikari
from lightbulb import plugins

from modmail import Config
from modmail.utils import helpers

if t.TYPE_CHECKING:
    from lightbulb.app import BotApp


plugin = plugins.Plugin("Mail", include_datastore=True)


@plugin.listener(hikari.StartedEvent)
async def on_started(event: hikari.StartedEvent) -> None:
    plugin.d.mail_channel = await plugin.bot.rest.fetch_channel(Config.MAIL_CHANNEL_ID)


@plugin.listener(hikari.DMMessageCreateEvent)
async def on_dm_message_create(event: hikari.DMMessageCreateEvent) -> None:
    if event.message.author.is_bot:
        return

    if job := plugin.bot.d.scheduler.get_job(f"{event.message.author.id}"):
        await event.message.respond(
            "Sorry, you're on cooldown! You can send another message "
            f"<t:{int(job.next_run_time.timestamp())}:R>."
        )
        return

    if not 50 <= len(event.message.content) < 1_000:
        await event.message.respond(
            "Your message should be between 50 and 1,000 characters long."
        )
        return

    member = plugin.bot.cache.get_guild(Config.GUILD_ID).get_member(event.author.id)

    embed = (
        hikari.Embed(
            title="Message",
            colour=helpers.choose_colour(),
            timestamp=dt.datetime.now().astimezone(),
        )
        .set_thumbnail(member.avatar_url)
        .set_author(name="Modmail")
        .set_footer(text=f"ID: {event.message.id}")
        .add_field("Member", f"{member.display_name} (ID: {member.id})")
        .add_field("Message", event.message.content)
    )

    if event.message.attachments:
        embed.set_image(event.message.attachments[0])

    await plugin.d.mail_channel.send(embed)
    await event.message.respond(
        "Message sent! If needed, a moderator will DM you regarding this issue. You'll "
        "need to wait 15 minutes before sending another message."
    )

    plugin.bot.d.scheduler.add_job(
        lambda: None,
        id=f"{event.message.author.id}",
        next_run_time=dt.datetime.utcnow() + dt.timedelta(seconds=900),
    )


@plugin.listener(hikari.GuildMessageCreateEvent)
async def on_guild_message_create(event: hikari.GuildMessageCreateEvent) -> None:
    if event.message.author.is_bot:
        return

    if (
        plugin.bot.get_me().id not in event.message.mentions.users
        or Config.STAFF_ROLE_ID in event.member.role_ids
    ):
        return

    await event.message.delete()
    try:
        await event.author.send(event.message.content)
        flavour = "but sent it to you via DM in case you wish to reuse it."
    except hikari.ForbiddenError:
        flavour = (
            "but unfortunately could not send it via DM to reuse as your privacy "
            "settings prevent it."
        )

    m = await event.message.respond(
        f"You need to submit reports by DM. I deleted your message, {flavour}."
    )
    await asyncio.sleep(10)
    await m.delete()


def load(bot: "BotApp") -> None:
    bot.add_plugin(plugin)


def unload(bot: "BotApp") -> None:
    bot.remove_plugin(plugin)
