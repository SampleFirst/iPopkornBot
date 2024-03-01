from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import ChatPrivileges
from info import ADMINS

@Client.on_message(filters.command("addadmin") & filters.private)
async def add_admin(client, message):
    if message.from_user.id not in ADMINS:
        await message.reply("You must be an admin to use this command.")
        return

    if len(message.command) != 2:
        await message.reply("Usage: /addadmin user_id")
        return

    user_id = int(message.command[1])

    try:
        chat_id = message.chat.id
        chat_info = await client.get_chat(chat_id)
    except Exception as e:
        await message.reply(f"Error: {str(e)}")
        return

    if chat_info.type == "channel":
        try:
            await client.promote_chat_member(
                chat_id,
                user_id,
                privileges=ChatPrivileges(
                    can_change_info=True,
                    can_post_messages=True,
                    can_edit_messages=True,
                    can_delete_messages=True,
                    can_invite_users=True,
                    can_manage_chat=True,
                    can_promote_members=True
                ),
            )
            await message.reply("User added as an admin in the channel with specified privileges.")
        except UserNotParticipant:
            await message.reply("The user must be a member of the channel to use this command.")
        except Exception as e:
            await message.reply(f"An error occurred: {str(e)}")

    elif chat_info.type == "group":
        try:
            await client.promote_chat_member(
                chat_id,
                user_id,
                privileges=ChatPrivileges(
                    can_change_info=True,
                    can_delete_messages=True,
                    can_restrict_members=True,
                    can_promote_members=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                    can_manage_chat=True
                ),
            )
            await message.reply("User added as an admin in the group with specified privileges.")
        except UserNotParticipant:
            await message.reply("The user must be a member of the group to use this command.")
        except Exception as e:
            await message.reply(f"An error occurred: {str(e)}")
