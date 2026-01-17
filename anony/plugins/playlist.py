# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import filters, types

from anony import app, db, yt


@app.on_message(filters.command(["ekle", "cikar"]) & ~app.bl_users)
async def _playlist_func(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text("Bir şarkı adı ver.")
    query = m.text.split(None, 1)[1]
    srch = await yt.search(query, 0)
    plist = await db.get_playlist(m.from_user.id, ids=True)

    if m.command[0] == "ekle":
        if plist and srch.id in plist:
            return await m.reply_text("Şarkı zaten çalma listesinde.")
        await db.add_track(m.from_user.id, srch.id, srch.title)
        await m.reply_text(f"Çalma listesine eklendi: {srch.title}")
    else:
        if not plist:
            return await m.reply_text("Şarkı çalma listesinde değil.")
        if srch.id not in plist:
            return await m.reply_text("Şarkı çalma listesinde değil.")
        await db.rm_track(m.from_user.id, srch.id)
        await m.reply_text(f"Çalma listesinden kaldırıldı: {srch.title}")
