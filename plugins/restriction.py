# restriction.py

import asyncio
import logging
from pyrogram import Client, filters, enums
from pyrogram.enums import MessageEntityType
from info import ADMINS, LOG_CHANNEL

# Define allowed entity types (adjust as needed)
allowed_entity_types = [
    MessageEntityType.MENTION,
    MessageEntityType.HASHTAG,
    MessageEntityType.CASHTAG,
    MessageEntityType.BOT_COMMAND,
    MessageEntityType.URL,
    MessageEntityType.EMAIL,
    MessageEntityType.PHONE_NUMBER,
    MessageEntityType.BOLD,
    MessageEntityType.ITALIC,
    MessageEntityType.UNDERLINE,
    MessageEntityType.STRIKETHROUGH,
    MessageEntityType.SPOILER,
    MessageEntityType.CODE,
    MessageEntityType.PRE,
    MessageEntityType.BLOCKQUOTE,
    MessageEntityType.TEXT_LINK,
    MessageEntityType.TEXT_MENTION,
    MessageEntityType.CUSTOM_EMOJI,
]


@Client.on_message(filters.group & filters.text & filters.incoming)
async def restrict_entity(client, message):
    """
    Restricts links and logs deleted messages in a group, including additional information.

    Args:
        client: The Pyrogram client instance.
        message: The incoming message object.
    """
    if message.entities is None:
        return  # Skip processing if there are no entities

    grp_id = message.chat.id
    title = message.chat.title
    user_id = message.from_user.id

    st = await client.get_chat_member(grp_id, userid)
    if (
        st.status != enums.ChatMemberStatus.ADMINISTRATOR
        and st.status != enums.ChatMemberStatus.OWNER
        and str(userid) not in ADMINS
    ):
        return  # Skip processing for admins or owners
        
    deleted_entities = []
    for entity in message.entities:
        if entity.type in allowed_entity_types:  # Use a defined list
            deleted_entities.append(entity.type)  # Track deleted entities
        else:
            return  # Skip processing if message contains entities not in allowed_entity_types

    if deleted_entities:
        # Construct formatted log message with specific information
        log_message = (
            f"#message_delete 🗑\n\n"
            f"● Chat id: <code>{grp_id}</code>\n"
            f"● Chat: @{message.chat.username}\n"
            f"● Chat title: {title}\n\n"
            f"● User id: <code>{user_id}</code>\n"
            f"● User: @{message.from_user.username}\n\n"
            f"● Text: {message.text}"
        )
        for entity_type in deleted_entities:
            log_message += f"\n\n● Entity Type: {entity_type}"

        try:
            # Delete the message, handling potential exceptions
            await message.delete()
            await client.send_message(LOG_CHANNEL, log_message)
        except Exception as e:
            logging.error(f"Error deleting message: {e}")
            
            
