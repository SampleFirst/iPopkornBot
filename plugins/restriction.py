import asyncio
import time
from pyrogram import Client, filters, enums
from pyrogram.types import ChatPermissions
from info import ADMINS, LOG_CHANNEL
from datetime import datetime as date

BANNED_WORDS = ["join", "bio", "spam"]

user_violat = {}

async def restrict_links(client, message):
    text = message.text
    username = message.from_user.username
    datetime_now = date.now().strftime("%Y-%m-%d %H:%M:%S")
    permissions = ChatPermissions(can_send_messages=False)

    if "http" in text or "https" in text:
        try:
            user_id = message.from_user.id
            if user_id not in user_violat:
                user_violat[user_id] = 1
                ban_duration = 1 * 3600 # Ban for 1 hour
            else:
                user_violat[user_id] += 1
                if user_violat[user_id] == 2:
                    ban_duration = 6 * 3600  # Ban for 6 hours
                elif user_violat[user_id] >= 3:
                    ban_duration = 0  # Permanent ban
    
            await message.delete()
            link = text if "http" in text else None
            caption = (
                f"**Third-party link detected:**\n"
                f"Link: {link}\n"
                f"User: @{username}\n"
                f"Group Id: {message.chat.id}\n"
                f"Group Name: {message.chat.title}\n"
                f"Ban Count: {user_violat[user_id]}\n"
                f"Date and Time: {datetime_now}"
            )
    
            if ban_duration > 0:
                await client.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=message.from_user.id,
                    permissions=permissions,
                    until_date=ban_duration,
                )
                await client.send_message(
                    chat_id=LOG_CHANNEL,
                    text=caption
                )
                warning_message = await message.reply_text(f"⚠️ Warning: Sending third-party links is not allowed in this group. You are banned for {ban_duration} hours.")
                await asyncio.sleep(5)
                await warning_message.delete()
            else:
                await client.ban_chat_member(
                    chat_id=message.chat.id,
                    user_id=message.from_user.id
                )
                await client.send_message(
                    chat_id=LOG_CHANNEL,
                    text=caption
                )
                warning_message = await message.reply_text("⚠️ Warning: Sending third-party links is not allowed in this group. You are permanently banned.")
                await asyncio.sleep(5)
                await warning_message.delete()
                
        except Exception as e:
            print(f"Error restricting link: {e}")


async def restrict_telegram_links(client, message):
    text = message.text
    username = message.from_user.username
    datetime_now = date.now().strftime("%Y-%m-%d %H:%M:%S")
    permissions = ChatPermissions(can_send_messages=False)

    if "@" in text or "t.me/" in text:
        try:
            user_id = message.from_user.id
            if user_id not in user_violat:
                user_violat[user_id] = 1
                ban_duration = 1 * 3600  # Ban for 6 hours
            else:
                user_violat[user_id] += 1
                if user_violat[user_id] == 2:
                    ban_duration = 6 * 3600  # Ban for 6 hours
                elif user_violat[user_id] >= 3:
                    ban_duration = 0  # Permanent ban

            await message.delete()
            link = text if "t.me/" in text else None
            caption = (
                f"**Telegram Username or link detected:**\n"
                f"Link: {link}\n"
                f"User: @{username}\n"
                f"Group Id: {message.chat.id}\n"
                f"Group Name: {message.chat.title}\n"
                f"Ban Count: {user_violat[user_id]}\n"
                f"Date and Time: {datetime_now}"
            )

            if ban_duration > 0:
                await client.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=message.from_user.id,
                    permissions=permissions,
                    until_date=ban_duration,
                )
                await client.send_message(
                    chat_id=LOG_CHANNEL,
                    text=caption
                )
                warning_message = await message.reply_text(f"⚠️ Warning: Sending usernames or Telegram links is not allowed here. You are banned for {ban_duration} hours.")
                await asyncio.sleep(5)
                await warning_message.delete()
            else:
                await client.ban_chat_member(
                    chat_id=message.chat.id,
                    user_id=message.from_user.id
                )
                await client.send_message(
                    chat_id=LOG_CHANNEL,
                    text=caption
                )
                warning_message = await message.reply_text("⚠️ Warning: Sending Telegram links is not allowed here. You are permanently banned.")
                await asyncio.sleep(5)
                await warning_message.delete()
            
        except Exception as e:
            print(f"Error: {e}")


async def restrict_ban_words(client, message):
    text = message.text.lower()
    username = message.from_user.username
    datetime_now = date.now().strftime("%Y-%m-%d %H:%M:%S")
    permissions = ChatPermissions(can_send_messages=False)

    for banned_word in BANNED_WORDS:
        if banned_word in text:
            try:
                user_id = message.from_user.id
                if user_id not in user_violat:
                    user_violat[user_id] = 1
                    ban_duration = 1 * 3600  # Ban for 6 hours
                else:
                    user_violat[user_id] += 1
                    if user_violat[user_id] == 2:
                        ban_duration = 6 * 3600  # Ban for 6 hours
                    elif user_violat[user_id] >= 3:
                        ban_duration = 0  # Permanent ban

                await message.delete()
                caption = (
                    f"**Ban Word detected:**\n"
                    f"Ban Word: {banned_word}\n"
                    f"User: @{username}\n"
                    f"Group Id: {message.chat.id}\n"
                    f"Group Name: {message.chat.title}\n"
                    f"Ban Count: {user_violat[user_id]}\n"
                    f"Date and Time: {datetime_now}"
                )

                if ban_duration > 0:
                    await client.restrict_chat_member(
                        chat_id=message.chat.id,
                        user_id=message.from_user.id,
                        permissions=permissions,
                        until_date=ban_duration,
                    )
                    await client.send_message(
                        chat_id=LOG_CHANNEL,
                        text=caption
                    )
                    warning_message = await message.reply_text(f"⚠️ Warning: Please refrain from using banned words. You are banned for {ban_duration} hours.")
                    await asyncio.sleep(5)
                    await warning_message.delete()
                else:
                    await client.ban_chat_member(
                        chat_id=message.chat.id,
                        user_id=message.from_user.id
                    )
                    await client.send_message(
                        chat_id=LOG_CHANNEL,
                        text=caption
                    )
                    warning_message = await message.reply_text("⚠️ Warning: You are permanently banned.")
                    await asyncio.sleep(5)
                    await warning_message.delete()
            
            except Exception as e:
                print(f"Error: {e}")
                
