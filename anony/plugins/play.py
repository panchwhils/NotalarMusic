# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pathlib import Path

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
    filters.command(["play", "playforce", "vplay", "vplayforce"])
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
    video: bool = False,
    url: str = None,
) -> None:
    sent = await m.reply_text(m.lang["play_searching"])
    file = None
    mention = m.from_user.mention
    media = tg.get_media(m.reply_to_message) if m.reply_to_message else None
    tracks = []

    if url:
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

    elif media:
        setattr(sent, "lang", m.lang)
        file = await tg.download(m.reply_to_message, sent)

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
        reply_markup=buttons.playlist_mode(
            m.from_user.id,
            m.lang["audio"],
            m.lang["video"],
        ),
    )


@app.on_callback_query(filters.regex("add_playlist"))
@lang.language()
async def _add_playlist(_, cq: types.CallbackQuery):
    q, vid_id = cq.data.split()
    plist = await db.get_playlist(cq.from_user.id)

    if plist and vid_id in plist:
        return await cq.answer(cq.lang["playlist_del"], show_alert=True)

    await db.add_track(cq.from_user.id, vid_id)
    await cq.answer(cq.lang["playlist_add"], show_alert=True)


@app.on_callback_query(filters.regex("playlist"))
@lang.language()
async def _playlist_cb(_, query: types.CallbackQuery):
    ok, user_id, mode = query.data.split()
    user_id = int(user_id)
    mention = query.from_user.mention
    chat_id = query.message.chat.id
    video = mode == "video"

    if query.from_user.id != user_id:
        return await query.answer(query.lang["playlist_not_you"], show_alert=True)

    plist = await db.get_playlist(user_id)
    if not plist:
        return await query.answer(query.lang["playlist_empty"], show_alert=True)

    await query.answer(query.lang["playlist_fetch"], show_alert=True)
    await query.edit_message_text(query.lang["playlist_fetch"])
    tracks = [await yt.search(vid, 0, video=video, mention=mention) for vid in plist]
    if await db.get_call(chat_id):
        added = await playlist_to_queue(chat_id, tracks)
        await app.send_message(
            chat_id=chat_id,
            text=query.lang["playlist_queued"].format(len(tracks)) + added,
        )
    else:
        media = tracks[0]
        tracks.remove(media)
        media.message_id = query.message.id
        media.file_path = await yt.download(media.id, video=video)
        await anon.play_media(chat_id=chat_id, message=query.message, media=media)
        if tracks:
            added = playlist_to_queue(chat_id, tracks)
            await app.send_message(
                chat_id=chat_id,
                text=query.lang["playlist_queued"].format(len(tracks)) + added,
            )
