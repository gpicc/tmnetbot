from typing import Callable, Dict

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.types.user_and_chats.user import Link

from .. import filters as custom_filters
from ..helpers import get_documents_range, format_documents_list
from ..mongo import admins
from ..telegram import telegram


_mention_user: Callable[[Dict], str] = lambda c: Link.format(f"tg://user?id={c.get('user_id')}", c.get("name"), "html")

loading_admins = "\
Caricamento lista admin..."

admins_list = "\
Elenco degli admin:\n\n\n{admins} "


@telegram.on_message(filters.private & filters.command(["amministratori", "admins", "admin"]) & custom_filters.is_admin)
async def get_admins(_, message: Message):
    await _navigate(await message.reply_text(loading_admins))


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data.startswith(f"{admins.name}_nav_")))
async def get_admins_page(_, callback_query: CallbackQuery):
    offset = int(callback_query.data.rsplit('_', 1)[1])

    await callback_query.answer()

    await _navigate(callback_query.message, offset)


async def _navigate(message: Message, offset=0):
    documents, keyboard = get_documents_range(admins, offset)

    fmt_admins = format_documents_list(documents, lambda c: f"{_mention_user(c)}\n"
                                                            f"ID: {c.get('user_id')}")

    await message.edit_text(admins_list.format(admins=fmt_admins), reply_markup=keyboard)
