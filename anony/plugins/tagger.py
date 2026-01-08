# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import asyncio
from pyrogram import filters, types

from anony import app, lang
from anony.helpers import admin_check


@app.on_message(filters.command(["tagall"]) & filters.group & ~app.bl_users)
@lang.language()
@admin_check
async def _tagall(_, m: types.Message):
    members = [
        member async for member in app.get_chat_members(m.chat.id)
        if not member.user.is_bot
    ]

    reply = m.reply_to_message.id if m.reply_to_message else None
    count, text = 0, ""
    for member in members:
        if count == 5:
            await app.send_message(
                chat_id=m.chat.id,
                text=text,
                reply_to_message_id=reply,
            )
            count, text = 0, ""
            await asyncio.sleep(3)

        text += member.user.mention + " "
        count += 1
