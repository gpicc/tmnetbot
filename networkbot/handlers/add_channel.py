# tmnetbot - Telegram bot
# Copyright (C) 2020 Midblyte <https://github.com/Midblyte>
#
# This file is part of tmnetbot.
#
# tmnetbot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tmnetbot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tmnetbot.  If not, see <https://www.gnu.org/licenses/>.

from typing import Union, Iterable

from pyrogram import filters, Client
from pyrogram.errors import RPCError
from pyrogram.methods.chats.get_chat_members import Filters
from pyrogram.types import Message, Chat, ChatPreview, ChatMember

from .. import filters as custom_filters
from ..mongo import channels
from ..telegram import telegram


usage = "\
Uso: /aggiungi @Username\n\nAlias: /add, /inserisci"

unexisting_channel = "\
Canale inesistente"

not_a_channel = "\
Non è un canale"

im_not_admin = "\
Non sono admin di quel canale"

already_in_list_channel = "\
Il canale è già nella lista."

successfully_added = "\
Inserito {} ({})."


@telegram.on_message(filters.private & filters.text & filters.command(["add", "aggiungi", "inserisci"]) &
                     custom_filters.is_admin)
async def add_channel(client: Client, message: Message):
    if ' ' not in message.text:
        return await message.reply_text(usage)

    channel_as_text = message.text.split(' ')[1]

    try:
        channel: Union[Chat, ChatPreview] = await client.get_chat(channel_as_text)
    except RPCError:
        return await message.reply_text(unexisting_channel)

    if channel.type != "channel":
        return await message.reply_text(not_a_channel)

    try:
        channel_admins: Iterable[ChatMember] = filter(lambda m: not (m.user.is_deleted or m.user.is_bot),
                                                      await channel.get_members(filter=Filters.ADMINISTRATORS))
    except RPCError:
        return await message.reply_text(im_not_admin)

    if channels.find_one({"channel_id": channel.id}):
        return await message.reply_text(already_in_list_channel)

    channels.insert_one({"channel_id": channel.id,
                         "name": channel.title,
                         "last_send": None,
                         "delta": None,
                         "administrators": list(map(lambda a: a.user.id, channel_admins)),
                         "scheduling": {
                             "in_queue": False,
                             "message_id": None,
                             "time_from": None,
                             "time_to": None
                         }})

    await message.reply_text(successfully_added.format(channel.title, channel.id))
