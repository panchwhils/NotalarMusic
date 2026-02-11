# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import random
import asyncio
from pyrogram import enums, filters, types

from anony import app, db, lang, queue
from anony.helpers import admin_check


running = []
emojis = ["🤞", "💕", "😘", "🙌", "😎", "👌", "😊", "❤️", "😍"]
greets = [
    "𝐒𝐞𝐧 𝐲𝐚𝐳ı𝐧𝐜𝐚 𝐡𝐞𝐫 ş𝐞𝐲 𝐛𝐢𝐫𝐚𝐳 𝐝𝐚𝐡𝐚 𝐬𝐚𝐤𝐢𝐧, 𝐛𝐢𝐫𝐚𝐳 𝐝𝐚𝐡𝐚 𝐠ü𝐳𝐞𝐥 𝐨𝐥𝐮𝐲𝐨𝐫 🌙",
    "𝐁𝐚𝐳ı 𝐢𝐧𝐬𝐚𝐧𝐥𝐚𝐫 𝐤𝐨𝐧𝐮ş𝐦𝐚𝐝𝐚𝐧 𝐛𝐢𝐥𝐞 𝐡𝐮𝐳𝐮𝐫 𝐯𝐞𝐫𝐢𝐫, 𝐬𝐞𝐧 𝐨𝐧𝐥𝐚𝐫𝐝𝐚𝐧𝐬ı𝐧 ✨",
    "𝐁𝐢𝐫 𝐦𝐞𝐬𝐚𝐣ı𝐧, 𝐮𝐳𝐮𝐧 𝐛𝐢𝐫 𝐠ü𝐧ü𝐧 𝐲𝐨𝐫𝐠𝐮𝐧𝐥𝐮ğ𝐮𝐧𝐮 𝐚𝐥ı𝐩 𝐠ö𝐭ü𝐫ü𝐲𝐨𝐫 💫",
    "𝐀𝐝ı𝐧 𝐠𝐞ç𝐭𝐢ğ𝐢 𝐚𝐧𝐝𝐚 𝐤𝐚𝐥𝐛𝐢𝐦 𝐬𝐞𝐛𝐞𝐩𝐬𝐢𝐳𝐜𝐞 𝐠ü𝐥ü𝐦𝐬ü𝐲𝐨𝐫 ❤️",
    "𝐒𝐞𝐬𝐬𝐢𝐳𝐥𝐢ğ𝐢𝐧 𝐛𝐢𝐥𝐞 𝐛𝐢𝐫 𝐚𝐧𝐥𝐚𝐦ı 𝐯𝐚𝐫𝐬𝐚, 𝐬𝐞𝐧𝐢𝐧𝐤𝐢 ç𝐨𝐤 𝐠ü𝐳𝐞𝐥 🌌",
    "𝐇𝐞𝐫𝐤𝐞𝐬 𝐠𝐞𝐥𝐢𝐫 𝐠𝐞ç𝐞𝐫 𝐚𝐦𝐚 𝐛𝐚𝐳ı 𝐢𝐬𝐢𝐦𝐥𝐞𝐫 𝐢𝐳 𝐛ı𝐫𝐚𝐤ı𝐫, 𝐬𝐞𝐧𝐢𝐧𝐤𝐢 𝐠𝐢𝐛𝐢 🌿",
    "𝐙𝐚𝐦𝐚𝐧 𝐲𝐚𝐯𝐚ş𝐥𝐚𝐝ığ𝐢𝐧𝐝𝐚 𝐚𝐤𝐥ı𝐦𝐚 𝐠𝐞𝐥𝐞𝐧 𝐢𝐥𝐤 𝐝𝐞𝐭𝐚𝐲 𝐬𝐞𝐧𝐬𝐢𝐧 🌙",
    "𝐊𝐞𝐥𝐢𝐦𝐞𝐥𝐞𝐫 𝐲𝐞𝐭𝐦𝐞𝐝𝐢ğ𝐢𝐧𝐝𝐞 𝐛𝐢𝐥𝐞 𝐡𝐢𝐬𝐬𝐞𝐭𝐭𝐢𝐫𝐞𝐧 𝐢𝐧𝐬𝐚𝐧𝐥𝐚𝐫𝐝𝐚𝐧 𝐛𝐢𝐫𝐢𝐬𝐢𝐧 ✨",
    "𝐁𝐮 𝐬𝐚𝐭ı𝐫𝐥𝐚𝐫ı𝐧 𝐢ç𝐢𝐧𝐝𝐞 𝐛𝐢𝐫𝐚𝐳 𝐡𝐮𝐳𝐮𝐫 𝐯𝐚𝐫𝐬𝐚, 𝐬𝐞𝐛𝐞𝐛𝐢 𝐬𝐞𝐧𝐬𝐢𝐧 💫",
    "𝐁𝐚𝐳𝐞𝐧 𝐛𝐢𝐫 𝐢𝐬𝐦𝐢𝐧 𝐚ğ𝐢𝐫𝐥ığ𝐢 𝐨𝐥𝐮𝐫, 𝐬𝐞𝐧𝐢𝐧𝐤𝐢 𝐤𝐚𝐥𝐛𝐢𝐦𝐞 𝐢𝐲𝐢 𝐠𝐞𝐥𝐢𝐲𝐨𝐫 ❤️",
    "𝐆𝐞𝐜𝐞𝐧𝐢𝐧 𝐨𝐫𝐭𝐚𝐬ı𝐧𝐝𝐚 𝐛𝐢𝐥𝐞 𝐢ç𝐢𝐦𝐢 ı𝐬ı𝐭𝐚𝐧 𝐛𝐢𝐫 𝐬𝐚𝐤𝐢𝐧𝐥𝐢ğ𝐢𝐧 𝐯𝐚𝐫 🌌",
    "𝐇𝐞𝐫𝐤𝐞𝐬𝐢𝐧 𝐟𝐚𝐫𝐤 𝐞𝐭𝐦𝐞𝐝𝐢ğ𝐢 𝐝𝐞𝐭𝐚𝐲𝐥𝐚𝐫ı 𝐟𝐚𝐫𝐤 𝐞𝐭𝐭𝐢𝐫𝐞𝐧 𝐛𝐢𝐫𝐢𝐬𝐢𝐧 🌿",
    "𝐕𝐚𝐫𝐥ığ𝐢𝐧, 𝐨𝐫𝐭𝐚𝐦ı 𝐬𝐞𝐬𝐬𝐢𝐳𝐜𝐞 𝐠ü𝐳𝐞𝐥𝐥𝐞ş𝐭𝐢𝐫𝐢𝐲𝐨𝐫 🌙",
    "𝐀𝐧𝐥𝐚𝐭𝐦𝐚𝐲𝐚 𝐠𝐞𝐫𝐞𝐤 𝐤𝐚𝐥𝐦𝐚𝐝𝐚𝐧 𝐚𝐧𝐥𝐚şı𝐥𝐚𝐛𝐢𝐥𝐞𝐧 𝐧𝐚𝐝𝐢𝐫 𝐢𝐧𝐬𝐚𝐧𝐥𝐚𝐫𝐝𝐚𝐧𝐬ı𝐧 ✨",
    "𝐁𝐚𝐳ı 𝐢𝐬𝐢𝐦𝐥𝐞𝐫 𝐬𝐚𝐝𝐞𝐜𝐞 𝐲𝐚𝐳ı𝐥ı𝐫, 𝐛𝐚𝐳ı𝐥𝐚𝐫ı 𝐡𝐢𝐬𝐬𝐞𝐝𝐢𝐥𝐢𝐫… 𝐬𝐞𝐧𝐢𝐧𝐤𝐢 𝐠𝐢𝐛𝐢 💫",
    "𝐊𝐨𝐧𝐮ş𝐦𝐚𝐬𝐚𝐧 𝐛𝐢𝐥𝐞 𝐢𝐳 𝐛ı𝐫𝐚𝐤𝐚𝐧 𝐛𝐢𝐫 𝐝𝐮𝐫𝐮ş𝐮𝐧 𝐯𝐚𝐫 ❤️",
    "𝐈ç𝐢𝐦𝐝𝐞 𝐠ü𝐳𝐞𝐥 𝐛𝐢𝐫 𝐡𝐢𝐬 𝐮𝐲𝐚𝐧𝐝ı𝐫𝐚𝐧 𝐧𝐚𝐝𝐢𝐫 𝐬𝐚𝐭ı𝐫𝐥𝐚𝐫𝐝𝐚𝐧𝐬ı𝐧 🌌",
    "𝐙𝐚𝐦𝐚𝐧ı𝐧 𝐤𝐚𝐫𝐦𝐚ş𝐚𝐬ı𝐧𝐝𝐚 𝐬𝐚𝐤𝐢𝐧 𝐛𝐢𝐫 𝐝𝐞𝐭𝐚𝐲 𝐠𝐢𝐛𝐢𝐬𝐢𝐧 🌿",
    "𝐇𝐞𝐫 ş𝐞𝐲 𝐠𝐞ç𝐢𝐜𝐢 𝐚𝐦𝐚 𝐡𝐢𝐬𝐬𝐞𝐭𝐭𝐢𝐫𝐝𝐢𝐤𝐥𝐞𝐫𝐢𝐧 𝐤𝐚𝐥ı𝐜ı 🌙",
    "𝐁𝐮 𝐦𝐞𝐬𝐚𝐣ı𝐧 𝐢ç𝐢𝐧𝐝𝐞 𝐛𝐢𝐫𝐚𝐳 𝐤𝐚𝐥𝐩 𝐯𝐚𝐫𝐬𝐚, 𝐬𝐞𝐛𝐞𝐛𝐢 𝐬𝐞𝐧𝐬𝐢𝐧 ✨"
]


@app.on_message(filters.command(["davet"]) & filters.group & ~app.bl_users)
@lang.language()
@admin_check
async def _vctag(_, m: types.Message):
    if not await db.get_call(m.chat.id):
        return await m.reply_text(m.lang["not_playing"])

    if m.chat.id in running:
        return await m.reply_text("Etiketleme işlemi zaten çalışıyor.")

    await m.reply_text("Etiketleme işlemi başlatıldı.")
    running.append(m.chat.id)

    members = [
        member async for member in app.get_chat_members(m.chat.id, limit=40)
        if not member.user.is_bot
    ]

    media = queue.get_current(m.chat.id)
    vc_text = f"<u><b>Neredesiniz ya? Video sohbete katılsanıza.</b></u>\n\n<b>Çalıyor: {media.title}</b>\n\n"
    count, text = 0, ""
    for member in members:
        if m.chat.id not in running:
            break

        count += 1
        text += member.user.mention + " "
        if count == 5:
            await app.send_message(
                chat_id=m.chat.id,
                text=vc_text + text,
            )
            count, text = 0, ""
            await asyncio.sleep(3)

    if count > 0:
        await app.send_message(
            chat_id=m.chat.id,
            text=vc_text + text,
        )
    if m.chat.id in running: running.remove(m.chat.id)


@app.on_message(filters.command(["utag", "atag", "etag", "gtag", "bitir"]) & filters.group & ~app.bl_users)
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
    gtag = m.command[0][0] == "g"
    count, text, etext = 0, "", ""
    if len(m.command) > 1 and not emoji:
        etext = m.text.split(None, 1)[1].strip()
    reply = m.reply_to_message.id if m.reply_to_message else None

    for member in members:
        if m.chat.id not in running:
            break

        count += 1
        if member.user.username and not emoji:
            user = ("@" + member.user.username)
        else:
            user = member.user.mention
            if emoji:
                user = user(random.choice(emojis))
        text += user + " "

        if count == 5:
            if gtag:
                etext = random.choice(greets)
            await app.send_message(
                chat_id=m.chat.id,
                text=f"{etext}\n{text}".strip(),
                reply_to_message_id=reply,
            )
            await asyncio.sleep(3)
            count, text = 0, ""
    if count > 0:
        if gtag:
            etext = random.choice(greets)
        await app.send_message(
            chat_id=m.chat.id,
            text=f"{etext}\n{text}".strip(),
            reply_to_message_id=reply,
        )
    if m.chat.id in running: running.remove(m.chat.id)
