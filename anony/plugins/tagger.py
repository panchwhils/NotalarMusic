# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import random
import asyncio
from pyrogram import enums, filters, types

from anony import app, lang
from anony.helpers import admin_check


running = []
emojis = ["🤞", "💕", "😘", "🙌", "😎", "👌", "😊", "❤️", "😍"]


@app.on_message(filters.command(["utag", "atag", "etag", "bitir"]) & filters.group & ~app.bl_users)
@lang.language()
@admin_check
async def _tagall(_, m: types.Message):
    if m.command[0] == "bitir":
        if m.chat.id not in running:
            return await m.reply_text("Etiketleme işlemi çalışmıyor.")
        running.remove(m.chat.id)
        return await m.reply_text("Etiketleme işlemi durduruldu.")

    if m.chat.id in running:
        return await m.reply_text("Etiketleme işlemi zaten çalışıyor.")

    await m.reply_text("Etiketleme işlemi başlatıldı.")
    running.append(m.chat.id)

    filter = enums.ChatMembersFilter.SEARCH
    if m.command[0] == "atag":
        filter = enums.ChatMembersFilter.ADMINISTRATORS

    members = [
        member async for member in app.get_chat_members(m.chat.id, filter=filter)
        if not member.user.is_bot
    ]

    emoji = m.command[0][0] == "e"
    text = ""
    if len(m.command) > 1 and not emoji:
        text = m.text.split(None, 1)[1].strip()
    reply = m.reply_to_message.id if m.reply_to_message else None

    for member in members:
        if m.chat.id not in running:
            break

        if member.user.username and not emoji:
            user = ("@" + member.user.username)
        else:
            user = member.user.mention
            if emoji:
                user = user(random.choice(emojis))

        await app.send_message(
            chat_id=m.chat.id,
            text=f"{text}\n{user}".strip(),
            reply_to_message_id=reply,
        )
        await asyncio.sleep(3)
    if m.chat.id in running: running.remove(m.chat.id)
