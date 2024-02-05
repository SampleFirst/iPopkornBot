import asyncio
import time
from pyrogram import Client, filters, enums
from info import ADMINS, LOG_CHANNEL
from datetime import datetime as date

BANNED_WORDS = ["join", "bio", "spam"]

user_violat = {}

@Client.on_message(filters.group & filters.text & filters.regex(r"https?://[^\s]+"))
async def restrict_links(client, message):
    link = message.text
    username = message.from_user.username
    datetime = date.now().strftime("%Y-%m-%d %H:%M:%S")  # Fixed date formatting

    try:
        user_id = message.from_user.id
        if user_id not in user_violat:
            user_violat[user_id] = 1
            ban_duration = 1 * 3600  # Ban for 1 hour
        else:
            user_violat[user_id] += 1
            if user_violat[user_id] == 2:
                ban_duration = 6 * 3600  # Ban for 6 hours
            elif user_violat[user_id] >= 3:  # Fixed syntax error in this line
                ban_duration = 0  # Permanent ban

        await message.delete()
        if ban_duration > 0:
            await message.reply_text(f"Sending third-party links is not allowed in this group. You are banned for {ban_duration} hours.")
            await client.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=message.from_user.id,
                ban_duration=ban_duration  # Fixed parameter name
            )
        else:
            await message.reply_text("Sending third-party links is not allowed in this group. You are permanently banned.")
            await client.ban_chat_member(
                chat_id=message.chat.id,
                user_id=message.from_user.id
            )

        await client.send_message(
            LOG_CHANNEL,
            f"**Third-party link detected:**\n"
            f"Link: {link}\n"
            f"User: @{username}\n"
            f"Ban Count: {ban_duration}\n"
            f"Date and Time: {datetime}",
        )

    except Exception as e:
        print(f"Error restricting link: {e}")


@Client.on_message(filters.group & filters.text & filters.incoming)
async def restrict_username_links(client, message):
    text = message.text
    username = message.from_user.username
    datetime = date.now().strftime("%Y-%m-%d %H:%M:%S")  # Fixed date formatting

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
                elif user_violat[user_id] >= 3:  # Fixed syntax error in this line
                    ban_duration = 0  # Permanent ban

            await message.delete()
            if ban_duration > 0:
                await message.reply_text(f"Sending usernames or Telegram links is not allowed here. You are banned for {ban_duration} hours.")
                await client.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=message.from_user.id,
                    ban_duration=ban_duration  # Fixed parameter name
                )
            else:
                await message.reply_text("Sending usernames or Telegram links is not allowed here. You are permanently banned.")
                await client.ban_chat_member(
                    chat_id=message.chat.id,
                    user_id=message.from_user.id
                )

            link = text if "t.me/" in text else None
            await client.send_message(
                LOG_CHANNEL,
                f"**Telegram Username or link detected:**\n"
                f"Link: {link}\n"
                f"User: @{username}\n"
                f"Ban Count: {ban_duration}\n"
                f"Date and Time: {datetime}",
            )
        except Exception as e:
            print(f"Error: {e}")


@Client.on_message(filters.group & filters.text & filters.incoming)
async def restrict_ban_words(client, message):
    text = message.text.lower()
    username = message.from_user.username
    datetime = date.now().strftime("%Y-%m-%d %H:%M:%S")  # Fixed date formatting

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
                    elif user_violat[user_id] >= 3:  # Fixed syntax error in this line
                        ban_duration = 0  # Permanent ban

                await message.delete()
                if ban_duration > 0:
                    await message.reply_text(f"⚠️ Warning: Please refrain from using banned words. You are banned for {ban_duration} hours.")
                    await client.restrict_chat_member(
                        chat_id=message.chat.id,
                        user_id=message.from_user.id,
                        ban_duration=ban_duration  # Fixed parameter name
                    )
                else:
                    await message.reply_text("⚠️ Warning: Please refrain from using banned words. You are permanently banned.")
                    await client.ban_chat_member(
                        chat_id=message.chat.id,
                        user_id=message.from_user.id
                    )

                await client.send_message(
                    LOG_CHANNEL,
                    f"**Ban Word detected:**\n"
                    f"Ban Word: {banned_word}\n"
                    f"User: @{username}\n"
                    f"Ban Count: {ban_duration}\n"
                    f"Date and Time: {datetime}",
                )
            except Exception as e:
                print(f"Error: {e}")
                
