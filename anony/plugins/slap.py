# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from random import choice, randint
from pyrogram import filters, types

from anony import app
from anony.helpers import utils


slaps = [
    "👋 ŞLAP! Öyle bir tokat ki Wi-Fi sinyali gitti.",
    "👋 ŞAPPAK! Tokadı yiyince düşünceler yeniden başlatıldı.",
    "👋 PAT! Bu tokat değil, sistem güncellemesi.",
    "👋 ŞLAK! Tokat geldi… ruh bedenden kısa süreliğine ayrıldı.",
    "👋 POF! Fizik kuralları bu tokattan sonra istifa etti.",
    "👋 ŞAP! Tokat o kadar sertti ki yankısı ertesi güne kaldı.",
    "👋 BAM! Bu bir tokat değil, ücretsiz karakter gelişimi.",
    "👋 ÇAT! Tokatlandıktan sonra “ben kimim?” sorgusu başladı.",
    "👋 ŞAPPAK! Yanaktan çok özgüvene geldi.",
    "👋 TOK! Tokat express teslim edildi. İade yok."
]


@app.on_message(filters.command(["slap"]) & filters.group & ~app.bl_users)
async def _slap(_, m: types.Message):
    if not m.from_user:
        return

    if user := await utils.extract_user(m):
        x = randint(0, 9)
        if x <= 5:
            await m.reply_text(choice(slaps))
        else:
            amt = randint(5, 200)
            usern = ("@" + user.username) if user.username else user.mention
            userm = ("@" + m.from_user.username) if m.from_user.username else m.from_user.mention
            await m.reply_text(f"{userm}, {usern}'nin yüzüne {amt}TL fırlattı!")
