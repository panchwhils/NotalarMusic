# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import filters, types

from anony import app, db, lang
from anony.helpers import can_manage_vc


@app.on_message(filters.command(["loop"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _loop(_, m: types.Message):
    if not await db.get_call(m.chat.id):
        return await m.reply_text(m.lang["not_playing"])

    if len(m.command) == 1 or not m.command[1].isdigit():
        return await m.reply_text(m.lang["loop_usage"])

    loop = int(m.command[1])
    await db.set_loop(m.chat.id, loop)
    await m.reply_text(m.lang["loop_set"].format(loop))
