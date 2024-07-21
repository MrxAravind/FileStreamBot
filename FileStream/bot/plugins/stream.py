import asyncio
from FileStream.bot import FileStream, multi_clients
from FileStream.utils.bot_utils import is_user_banned, is_user_exist, is_user_joined, gen_linkx, gen_link,is_channel_banned, is_channel_exist, is_user_authorized
from FileStream.utils.database import Database
from FileStream.utils.file_properties import get_file_ids, get_file_info
from FileStream.config import Telegram
from pyrogram import filters, Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums.parse_mode import ParseMode
db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)

@FileStream.on_message(
    filters.private
    & (
            filters.document
            | filters.video
            | filters.video_note
            | filters.audio
            | filters.voice
            | filters.animation
            | filters.photo
    ),
    group=4,
)
async def private_receive_handler(bot: Client, message: Message):
    if not await is_user_authorized(message):
        return
    if await is_user_banned(message):
        return
    
    await is_user_exist(bot, message)
    if Telegram.FORCE_SUB:
        if not await is_user_joined(bot, message):
            return
    try:
        inserted_id = await db.add_file(get_file_info(message))
        await get_file_ids(False, inserted_id, multi_clients, message)
        reply_markup, stream_text = await gen_link(_id=inserted_id)
        if message.document:          
           thumbnail_path = None
        elif message.photo:
           thumbnail_path = await bot.download_media(message.photo.file_id)
        elif message.video.thumbs:
            thumbnail_path = await bot.download_media(message.video.thumbs[0].file_id)
        if thumbnail_path:
            await bot.send_photo(
            chat_id=-1002239174542,
            photo=thumbnail_path,
            caption=stream_text,
            reply_markup=reply_markup)
        else:
               await bot.send_message(
               chat_id=-1002239174542,
               text=stream_text,
               reply_markup=reply_markup)
    except FloodWait as e:
        print(f"Sleeping for {str(e.value)}s")
        await asyncio.sleep(e.value)
        await bot.send_message(chat_id=Telegram.ULOG_CHANNEL,
                               text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.value)}s ғʀᴏᴍ [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n\n**ᴜsᴇʀ ɪᴅ :** `{str(message.from_user.id)}`",
                               disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)


@FileStream.on_message(
    filters.channel
    & ~filters.forwarded
    & ~filters.media_group
    & (
            filters.document
            | filters.video
            | filters.video_note
            | filters.audio
            | filters.voice
            | filters.photo
    )
)
async def channel_receive_handler(bot: Client, message: Message):
    if await is_channel_banned(bot, message) and message.chat_id != Telegram.FLOG_CHANNEL:
        return
    await is_channel_exist(bot, message)
    if message.chat.id == Telegram.ULOG_CHANNEL or message.chat.id == Telegram.FLOG_CHANNEL:
        return
    try:
        inserted_id = await db.add_file(get_file_info(message))
        await get_file_ids(False, inserted_id, multi_clients, message)
        reply_markup, stream_link = await gen_linkx(_id=inserted_id)
        if message.document:          
           thumbnail_path = None
        elif message.photo:
           thumbnail_path = await bot.download_media(message.photo.file_id)
        elif message.video.thumbs:
            thumbnail_path = await bot.download_media(message.video.thumbs[0].file_id)

        if thumbnail_path:
            await bot.send_photo(
            chat_id=-1002239174542,
            photo=thumbnail_path,
            caption=stream_link,
            reply_markup=reply_markup)
        else:
               await bot.send_message(
               chat_id=-1002239174542,
               text=stream_link,
               reply_markup=reply_markup)
    except FloodWait as w:
        print(f"Sleeping for {str(w.x)}s")
        await asyncio.sleep(w.x)
        await bot.send_message(chat_id=Telegram.ULOG_CHANNEL,
                               text=f"ɢᴏᴛ ғʟᴏᴏᴅᴡᴀɪᴛ ᴏғ {str(w.x)}s ғʀᴏᴍ {message.chat.title}\n\n**ᴄʜᴀɴɴᴇʟ ɪᴅ :** `{str(message.chat.id)}`",
                               disable_web_page_preview=True)
    except Exception as e:
        await bot.send_message(chat_id=Telegram.ULOG_CHANNEL, text=f"**#EʀʀᴏʀTʀᴀᴄᴋᴇʙᴀᴄᴋ:** `{e}`",
                               disable_web_page_preview=True)
        print(f"Cᴀɴ'ᴛ Eᴅɪᴛ Bʀᴏᴀᴅᴄᴀsᴛ Mᴇssᴀɢᴇ!\nEʀʀᴏʀ:  **Gɪᴠᴇ ᴍᴇ ᴇᴅɪᴛ ᴘᴇʀᴍɪssɪᴏɴ ɪɴ ᴜᴘᴅᴀᴛᴇs ᴀɴᴅ ʙɪɴ Cʜᴀɴɴᴇʟ!{e}**")

