import asyncio
from datetime import datetime as date
from database.users_chats_db import db
from pyrogram.types import ChatPermissions, Message
from info import ADMINS, LOG_CHANNEL

BANNED_WORDS = ["join", "bio", "spam"]

user_violations = {}


async def restrict_links(client, message):
    text = message.text
    username = message.from_user.username
    datetime_now = date.now().strftime("%Y-%m-%d %H:%M:%S")
    permissions = ChatPermissions(can_send_messages=False)

    if "http" in text or "https" in text:
        try:
            user_id = message.from_user.id
            ban_count = await db.user_latest_restrictions(user_id)
            if user_id not in user_violations:
                user_violations[user_id] = ban_count
            else:
                user_violations[user_id] += 1
                
            ban_count = user_violations[user_id]

            await db.add_user_restrictions(user_id, username, text, message.chat.id, message.chat.title, ban_count, datetime_now)
            await message.delete()
            link = text if "http" in text else None
            caption = (
                f"#link_detected:\n"
                f"Ban Link: {link}\n"
                f"Link text: {text}\n"
                f"User id: #{user_id}\n"
                f"User: @{username}\n"
                f"Group Id: {message.chat.id}\n"
                f"Group Name: {message.chat.title}\n"
                f"Ban Count: {ban_count}\n"
                f"Date and Time: {datetime_now}"
            )

            ban_duration = 1 * 3600 if ban_count == 1 else (6 * 3600 if ban_count == 2 else 0)
            
            if ban_duration > 0:
                await client.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=message.from_user.id,
                    permissions=permissions,
                    until_date=ban_duration,
                )
                warning_message = await message.reply_text(f"⚠️ Warning: Sending third-party links is not allowed in this group. You are banned for {ban_duration // 3600} hours.")
                log_message = await client.send_message(
                    chat_id=LOG_CHANNEL,
                    text=caption
                )
                await client.pin_chat_message(LOG_CHANNEL, log_message.message_id)
                await asyncio.sleep(5)
                await warning_message.delete()
            else:
                await client.ban_chat_member(
                    chat_id=message.chat.id,
                    user_id=message.from_user.id
                )
                warning_message = await message.reply_text("⚠️ Warning: Sending third-party links is not allowed in this group. You are permanently banned.")
                log_message = await client.send_message(
                    chat_id=LOG_CHANNEL,
                    text=caption
                )
                await client.pin_chat_message(LOG_CHANNEL, log_message.message_id)
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
            ban_count = await db.user_latest_restrictions(user_id)
            if user_id not in user_violations:
                user_violations[user_id] = ban_count
            else:
                user_violations[user_id] += 1
                
            ban_count = user_violations[user_id]

            await db.add_user_restrictions(user_id, username, text, message.chat.id, message.chat.title, ban_count, datetime_now)
            await message.delete()
            link = text if "t.me/" in text else None
            caption = (
                f"#tg_link_detected:\n"
                f"Link: {link}\n"
                f"Link text: {text}\n"
                f"User id: #{user_id}\n"
                f"User: @{username}\n"
                f"Group Id: {message.chat.id}\n"
                f"Group Name: {message.chat.title}\n"
                f"Ban Count: {ban_count}\n"
                f"Date and Time: {datetime_now}"
            )

            ban_duration = 1 * 3600 if ban_count == 1 else (6 * 3600 if ban_count == 2 else 0)
            
            if ban_duration > 0:
                await client.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=message.from_user.id,
                    permissions=permissions,
                    until_date=ban_duration,
                )
                warning_message = await message.reply_text(f"⚠️ Warning: Sending usernames or Telegram links is not allowed here. You are banned for {ban_duration // 3600} hours.")
                log_message = await client.send_message(
                    chat_id=LOG_CHANNEL,
                    text=caption
                )
                await client.pin_chat_message(LOG_CHANNEL, log_message.message_id)
                await asyncio.sleep(5)
                await warning_message.delete()
            else:
                await client.ban_chat_member(
                    chat_id=message.chat.id,
                    user_id=message.from_user.id
                )
                warning_message = await message.reply_text("⚠️ Warning: Sending Telegram links is not allowed here. You are permanently banned.")
                log_message = await client.send_message(
                    chat_id=LOG_CHANNEL,
                    text=caption
                )
                await client.pin_chat_message(LOG_CHANNEL, log_message.message_id)
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
                ban_count = await db.user_latest_restrictions(user_id)
                if user_id not in user_violations:
                    user_violations[user_id] = ban_count
                else:
                    user_violations[user_id] += 1
                
                ban_count = user_violations[user_id]

                await db.add_user_restrictions(user_id, username, text, message.chat.id, message.chat.title, ban_count, datetime_now)
                await message.delete()
                caption = (
                    f"#ban_word_detected:\n"
                    f"Ban Word: {banned_word}\n"
                    f"Word Text: {text}\n"
                    f"User id: #{user_id}\n"
                    f"User: @{username}\n"
                    f"Group Id: {message.chat.id}\n"
                    f"Group Name: {message.chat.title}\n"
                    f"Ban Count: {ban_count}\n"
                    f"Date and Time: {datetime_now}"
                )

                ban_duration = 1 * 3600 if ban_count == 1 else (6 * 3600 if ban_count == 2 else 0)
                
                if ban_duration > 0:
                    await client.restrict_chat_member(
                        chat_id=message.chat.id,
                        user_id=message.from_user.id,
                        permissions=permissions,
                        until_date=ban_duration,
                    )
                    warning_message = await message.reply_text(f"⚠️ Warning: Please refrain from using banned words. You are banned for {ban_duration // 3600} hours.")
                    log_message = await client.send_message(
                        chat_id=LOG_CHANNEL,
                        text=caption
                    )
                    await client.pin_chat_message(LOG_CHANNEL, log_message.message_id)
                    await asyncio.sleep(5)
                    await warning_message.delete()
                else:
                    await client.ban_chat_member(
                        chat_id=message.chat.id,
                        user_id=message.from_user.id
                    )
                    warning_message = await message.reply_text("⚠️ Warning: You are permanently banned.")
                    log_message = await client.send_message(
                        chat_id=LOG_CHANNEL,
                        text=caption
                    )
                    await client.pin_chat_message(LOG_CHANNEL, log_message.message_id)
                    await asyncio.sleep(5)
                    await warning_message.delete()
            except Exception as e:
                print(f"Error: {e}")
