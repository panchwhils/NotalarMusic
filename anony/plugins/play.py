# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic

import time
import asyncio
from pathlib import Path
from random import shuffle

from pyrogram import filters, types

from anony import anon, app, config, db, lang, queue, tg, yt
from anony.helpers import buttons, utils
from anony.helpers._play import checkUB


def playlist_to_queue(chat_id: int, tracks: list) -> str:
    text = "<blockquote expandable>"
    for track in tracks:
        pos = queue.add(chat_id, track)
        text += f"<b>{pos}.</b> {track.title}\n"
    text = text[:1948] + "</blockquote>"
    return text

@app.on_message(
    filters.command(["oynat", "playforce", "voynat", "vplayforce"])
    & filters.group
    & ~app.bl_users
)
@lang.language()
@checkUB
async def play_hndlr(
    _,
    m: types.Message,
    force: bool = False,
    m3u8: bool = False,
    spotify: bool = False,
    soundcloud: bool = False,
    video: bool = False,
    url: str = None,
) -> None:
    sent = await m.reply_text(m.lang["play_searching"])
    file = None
    mention = m.from_user.mention
    media = tg.get_media(m.reply_to_message) if m.reply_to_message else None
    tracks = []

    if media:
        setattr(sent, "lang", m.lang)
        file = await tg.download(m.reply_to_message, sent)

    elif spotify or soundcloud:
        result = await yt.fallen.get_title(url)
        if not result:
            return await sent.edit_text(m.lang["play_not_found"].format(config.SUPPORT_CHAT))
        file = await yt.search(result.get("title"), sent.id, video=video)
        if not file:
            return await sent.edit_text(m.lang["play_not_found"].format(config.SUPPORT_CHAT))
        file.title = result.get("title").title()
        file.url = result.get("url")
        if soundcloud:
            url = file.url
        file.thumbnail = result.get("thumbnail")
        file.duration_sec = result.get("duration")
        file.duration = time.strftime("%M:%S", time.gmtime(file.duration_sec))
        file.view_count = result.get("views")

    elif m3u8:
        file = await tg.process_m3u8(url, sent.id, video)

    elif url:
        if "playlist" in url:
            await sent.edit_text(m.lang["playlist_fetch"])
            tracks = await yt.playlist(
                config.PLAYLIST_LIMIT, mention, url, video
            )

            if not tracks:
                return await sent.edit_text(m.lang["playlist_error"])

            file = tracks[0]
            tracks.remove(file)
            file.message_id = sent.id
        else:
            file = await yt.search(url, sent.id, video=video)

        if not file:
            return await sent.edit_text(
                m.lang["play_not_found"].format(config.SUPPORT_CHAT)
            )

    elif len(m.command) >= 2:
        query = " ".join(m.command[1:])
        file = await yt.search(query, sent.id, video=video)
        if not file:
            return await sent.edit_text(
                m.lang["play_not_found"].format(config.SUPPORT_CHAT)
            )

    if not file:
        return await sent.edit_text(m.lang["play_usage"])

    if file.duration_sec > config.DURATION_LIMIT:
        return await sent.edit_text(
            m.lang["play_duration_limit"].format(config.DURATION_LIMIT // 60)
        )

    if await db.is_logger():
        await utils.play_log(m, file.title, file.duration)

    file.user = mention
    if force:
        queue.force_add(m.chat.id, file)
    else:
        position = queue.add(m.chat.id, file)

        if position != 0 or await db.get_call(m.chat.id):
            await sent.edit_text(
                m.lang["play_queued"].format(
                    position,
                    file.url,
                    file.title,
                    file.duration,
                    m.from_user.mention,
                ),
                reply_markup=buttons.play_queued(
                    m.chat.id, file.id, m.lang["play_now"]
                ),
            )
            if tracks:
                added = playlist_to_queue(m.chat.id, tracks)
                await app.send_message(
                    chat_id=m.chat.id,
                    text=m.lang["playlist_queued"].format(len(tracks)) + added,
                )
            return

    if not file.file_path:
        fname = f"downloads/{file.id}.{'mp4' if video else 'webm'}"
        if Path(fname).exists():
            file.file_path = fname
        else:
            await sent.edit_text(m.lang["play_downloading"])
            if soundcloud:
                file.file_path = await yt.download(url, video=False)
            else:
                file.file_path = await yt.download(file.id, video=video)

    await anon.play_media(chat_id=m.chat.id, message=sent, media=file)
    if not tracks:
        return
    added = playlist_to_queue(m.chat.id, tracks)
    await app.send_message(
        chat_id=m.chat.id,
        text=m.lang["playlist_queued"].format(len(tracks)) + added,
    )


@app.on_message(filters.command(["playlist"]) & filters.group & ~app.bl_users)
@lang.language()
async def _playlist(_, m: types.Message):
    await m.reply_text(
        text=m.lang["playlist_mode"],
        reply_markup=buttons.playlist_mode(m.from_user.id),
    )


@app.on_callback_query(filters.regex("playlist"))
@lang.language()
async def _playlist_cb(_, query: types.CallbackQuery):
    ok, user_id, mode = query.data.split()
    user_id = int(user_id)
    mention = query.from_user.mention
    chat_id = query.message.chat.id
    order = mode == "order"

    if query.from_user.id != user_id:
        return await query.answer(query.lang["playlist_not_you"], show_alert=True)

    plist = await db.get_playlist(user_id, ids=True)
    if not plist:
        return await query.answer(query.lang["playlist_empty"], show_alert=True)

    await query.answer(query.lang["playlist_fetch"], show_alert=True)
    await query.edit_message_text(query.lang["playlist_fetch"])
    tracks = [await yt.search(vid, 0, mention=mention) for vid in plist]
    if not order:
        shuffle(tracks)
    if await db.get_call(chat_id):
        added = playlist_to_queue(chat_id, tracks)
        await query.edit_message_text(query.lang["playlist_queued"].format(len(tracks)) + added)
    else:
        media = tracks[0]
        queue.add(chat_id, media)
        tracks.remove(media)
        media.message_id = query.message.id
        media.file_path = await yt.download(media.id, video=False)
        await anon.play_media(chat_id=chat_id, message=query.message, media=media)
        if tracks:
            added = playlist_to_queue(chat_id, tracks)
            await app.send_message(
                chat_id=chat_id,
                text=query.lang["playlist_queued"].format(len(tracks)) + added,
            )


channels = {
    "S Sport": "http://tr3.153689.xyz:80/AnsUcxM9zY/JSZnByRJrm/866987",
    "S Sport plus": "http://tr3.153689.xyz:80/AnsUcxM9zY/JSZnByRJrm/866990",
    "Ssport plus 2": "http://tr3.153689.xyz:80/AnsUcxM9zY/JSZnByRJrm/866991",
    "Ssport plus 3": "http://tr3.153689.xyz:80/AnsUcxM9zY/JSZnByRJrm/866992",
}
cnames = list(channels.keys())
clinks = list(channels.values())

@app.on_message(filters.command(["tv"]) & filters.group & ~app.bl_users)
async def _tv(_, m: types.Message):
    keyb = buttons.tv_streams(channels)
    await m.reply_text("Kanalı seçin ve oynatmaya başlamak için aşağıdaki düğmeye tıklayın:", reply_markup=keyb)


@app.on_callback_query(filters.regex("tv"))
async def _tv_cb(_, cq: types.CallbackQuery):
    await cq.answer("İşleniyor...", show_alert=True)
    data = cq.data.split()
    name = cnames[int(data[1])]
    link = clinks[int(data[1])]
    await cq.edit_message_text("İşleniyor...")
    file = await tg.process_m3u8(link, cq.message.id, video=True, title=name)
    file.user = cq.from_user.mention
    queue.force_add(cq.message.chat.id, file)
    try:
        await anon.play_media(chat_id=cq.message.chat.id, message=cq.message, media=file)
    except asyncio.TimeoutError:
        return await cq.edit_message_text("Dosyada ses kaynağı bulunamadı.")
