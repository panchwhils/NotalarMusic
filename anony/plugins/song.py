from pyrogram import filters, types

from anony import app, config, lang, yt
from anony.helpers import thumb


@app.on_message(filters.command(["indir"]) & ~app.bl_users)
@lang.language()
async def _song(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(m.lang["play_usage"].replace("play", "indir"))

    name = m.text.split(None, 1)[1]
    sent = await m.reply_text(m.lang["play_searching"])
    media = await yt.search(name, 0, video=False)
    if not media:
        return await m.reply_text(
            m.lang["play_not_found"].format(config.SUPPORT_CHAT)
        )

    await sent.edit_text(m.lang["play_downloading"])
    media.file_path = await yt.download(media.id, video=False, song=True)
    if not media.file_path:
        return await m.reply_text(m.lang["error_no_file"].format(config.SUPPORT_CHAT))

    keyb = types.InlineKeyboardMarkup(
        [[types.InlineKeyboardButton(text=m.lang["channel"], url=config.SUPPORT_CHANNEL)]]
    )
    _thumb = await thumb.save_thumb(f"cache/{media.id}.jpg", media.thumbnail)
    await m.reply_audio(
        audio=media.file_path,
        caption=media.title,
        duration=media.duration_sec,
        performer=media.channel_name,
        title=media.title,
        thumb=_thumb,
        reply_markup=keyb,
    )
    await sent.delete()

    try:
        __import__("os").remove(_thumb)
    except:
        pass
