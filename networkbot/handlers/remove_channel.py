from pyrogram import filters, Client
from pyrogram.errors import RPCError
from pyrogram.types import Message, Chat

from .add_channel import not_a_channel
from .. import filters as custom_filters
from ..mongo import channels
from ..telegram import telegram


usage = "\
Uso: /rimuovi @Username\n\nAlias: /remove, /rm"

successfully_removed = "\
Rimosso {} ({})."

unlisted_channel = "\
Il canale non è nella lista."


@telegram.on_message(filters.private & filters.text & filters.command(["remove", "rm", "rimuovi"]) &
                     custom_filters.is_admin)
async def remove_channel(client: Client, message: Message):
    if ' ' not in message.text:
        return await message.reply_text(usage)

    channel_as_text = message.text.split(' ')[1]

    try:
        channel: Chat = await client.get_chat(channel_as_text)
    except RPCError:
        return await message.reply_text(unlisted_channel)

    if channel.type != "channel":
        return await message.reply_text(not_a_channel)

    if channels.find_one_and_delete({"channel_id": channel.id}) is None:
        await message.reply_text(unlisted_channel)
    else:
        await message.reply_text(successfully_removed.format(channel.title, channel.id))
