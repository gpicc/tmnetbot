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

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup as Keyboard

from .. import filters as custom_filters
from ..utils.keyboards import select_double_time_keyboard, custom_btn, select_double_time_header, confirm_btn
from ..mongo import options, admins, options_collection
from ..telegram import telegram
from ..utils.time import fmt_mins

_PREFIX = "settings"

get_buttons = lambda: [
    [custom_btn('Network -> fascia oraria', _PREFIX, ['forward', 'tr', 'set',
                                                      options('time_range_start'), options('time_range_end')])],
    [custom_btn('Network -> distanziamento', _PREFIX, ['forward', 'nd', 'set', options('network_delta')])],
    [custom_btn('Canali -> distanziamento', _PREFIX, ['forward', 'cd', 'set', options('channels_delta')])]
]

settings_text = "\
Impostazioni"

select_time_range = "\
Fascia oraria consentita: {start} - {end}"

not_allowed = "\
Non sei amministratore del bot"

already_in_queue = "\
Spiacente, un messaggio è già in coda per l'invio."

back_to_menu = "\
Torna al menu"

settings_ok = lambda msg: msg.edit_text(text="Salvato",
                                        reply_markup=Keyboard([[custom_btn(back_to_menu, _PREFIX, ["menu"])]]))


@telegram.on_message(filters.private & filters.command(["settings", "impostazioni"]) & custom_filters.is_admin)
async def settings(_, message: Message):
    await message.reply_text(settings_text, reply_markup=Keyboard(get_buttons()))


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data.startswith(f"{_PREFIX}_menu")))
async def settings_menu(_, callback_query: CallbackQuery):
    await callback_query.message.edit_text(settings_text, reply_markup=Keyboard(get_buttons()))


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data.startswith(f"{_PREFIX}_forward_tr_set_")))
async def settings_forward_time_range_set(_, callback_query: CallbackQuery):
    await callback_query.answer()

    start, end = map(int, callback_query.data.rsplit('_', 2)[1:])

    time_keyboard = select_double_time_keyboard(f"{_PREFIX}", start, end, callback_query.data.split('_', 5)[1:4])

    fmt_text = select_time_range.format(start=fmt_mins(start), end=fmt_mins(end))

    await callback_query.message.edit_text(fmt_text, reply_markup=Keyboard([
        select_double_time_header(),
        *time_keyboard,
        [confirm_btn(_PREFIX, ['forward', 'tr', 'confirm', start, end])]
    ]))


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data.startswith(f"{_PREFIX}_forward_tr_confirm_")))
async def settings_forward_time_range_confirm(_, callback_query: CallbackQuery):
    await callback_query.answer()

    start, end = map(int, callback_query.data.rsplit('_', 2)[1:])

    if admins.find_one({"user_id": callback_query.from_user.id}) is None:
        return await callback_query.message.edit_text(not_allowed)

    options_collection.find_one_and_update({}, {"$set": {"time_range_start": start, "time_range_end": end}})

    await settings_ok(callback_query.message)


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data.startswith(f"{_PREFIX}_forward_nd_set_")))
async def settings_forward_network_delta_set(_, callback_query: CallbackQuery):
    await callback_query.answer()


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data.startswith(f"{_PREFIX}_forward_nd_confirm_")))
async def settings_forward_network_delta_confirm(_, callback_query: CallbackQuery):
    await callback_query.answer()

    await settings_ok(callback_query.message)


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data.startswith(f"{_PREFIX}_forward_cd_set_")))
async def settings_forward_channels_delta_set(_, callback_query: CallbackQuery):
    await callback_query.answer()


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data.startswith(f"{_PREFIX}_forward_cd_confirm_")))
async def settings_forward_channels_delta_confirm(_, callback_query: CallbackQuery):
    await callback_query.answer()

    await settings_ok(callback_query.message)
