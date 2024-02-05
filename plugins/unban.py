import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import ADMINS

@Client.on_message(filters.command("unbanall") & filters.chat(type=["group", "supergroup"]))
async def unban_all_members(client, message):
    chat_id = message.chat.id
    if message.from_user.id not in ADMINS:
        await message.reply_text("Only admins can use this command.")
        return

    try:
        chat = await client.get_chat(chat_id)

        # Get group data
        group_data = f"**Group ID:** {chat_id}\n**Group Name:** {chat.title}\n**Total Members:** {chat.members_count}\n**Total Banned Members:** {chat.banned_count}"

        # Create inline keyboard with "All Unban" button
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("All Unban", callback_data="unban_all")
                ]
            ]
        )

        await message.reply_text(group_data, reply_markup=keyboard)

    except Exception as e:
        await message.reply_text(f"Error getting group data: {e}")

@Client.on_callback_query(filters.regex("unban_all"))
async def handle_unban_all(client, query):
    chat_id = query.message.chat.id

    try:
        async for banned_member in client.iter_chat_members(chat_id, filter="banned"):
            await client.unban_chat_member(chat_id, banned_member.user.id)
            try:
                # Attempt to add member back to the group
                await client.add_chat_member(chat_id, user_id=banned_member.user.id)
            except Exception as e:
                # If adding back fails, send invite link
                await client.send_message(chat_id, f"Failed to add {banned_member.user.mention} back to the group. Sending invite link instead.")
                invite_link = await client.export_chat_invite_link(chat_id)
                await client.send_message(chat_id, f"Invite link: {invite_link}")

        await query.message.edit_text("All banned members have been unbanned and added back to the group.")

    except Exception as e:
        await query.message.edit_text(f"Error unbanning members: {e}")
