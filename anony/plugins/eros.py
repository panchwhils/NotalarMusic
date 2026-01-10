# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from random import choice, randint
from pyrogram import filters, types

from anony import app


temp = """
🏹 <b>Eros'un oku atıldı!</b> 💘

💑 <b>Aşıklar:</b>
{0} 💞 {1}

{2}
"""

texts = [
    "💥 Çok zor bir eşleşme! Ama aşkta her şey mümkün… belki mucize gerekir 😅",
    "💔 Düşük uyum. Anlaşmak için ciddi sabır ve emek şart.",
    "💞 Zayıf uyum. Doğru zamanda, doğru iletişimle biraz toparlanabilir.",
    "💝 Ortanın altı uyum. Emek verilirse ilerleme kaydedilebilir.",
    "💝 Orta düzey uyum. Dengede bir ilişki, ama çaba şart.",
    "💖 İyi bir uyumluluk! Birbirlerini mutlu etme potansiyelleri var.",
    "💖 Güzel bir eşleşme! Uyum yüksek, iletişim güçlü olabilir.",
    "💘 Çok iyi uyum! Birlikteyken işler genelde yolunda gider.",
    "💞 Harika bir eşleşme! Ruh eşi hissi verebilir ✨",
    "💍 Mükemmel uyum! Aşk, anlayış ve uyum zirvede 💖🔥"
]

@app.on_message(filters.command(["eros"]) & filters.group & ~app.bl_users)
async def _eros(_, m: types.Message):
    if not m.from_user:
        return

    members = [member async for member in app.get_chat_members(m.chat.id, limit=25)
               if not member.user.is_bot]
    m1, m2 = choice(members), choice(members)
    m1u = ("@" + m1.user.username) if m1.user.username else m1.user.mention
    m2u = ("@" + m2.user.username) if m2.user.username else m2.user.mention

    percent = randint(0, 100)
    index = min(percent // 10, 9)
    text = f"<b>Uyumluluk Oranı:</b> {percent}% {texts[index]}"
    await m.reply_text(temp.format(m1u, m2u, text))
