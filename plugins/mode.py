from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS

MAINTENANCE_MODE = False  # Default maintenance mode status (case-sensitive)


@Client.on_message(filters.command("mode") & filters.user(ADMINS))
async def maintenance_mode_options(client, message):
    if message.from_user.id in ADMINS:
        markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Mode", callback_data="mode_info"),
                    InlineKeyboardButton("ON" if MAINTENANCE_MODE else "OFF", callback_data="set_mode")
                ]
            ]
        )

        await message.reply_text("Maintenance mode options:", reply_markup=markup, quote=True)
    else:
        await message.reply_text("Unauthorized! Only admins can toggle maintenance mode.")

@Client.on_callback_query(filters.regex(r"^set_mode$") & filters.user(ADMINS))
async def set_maintenance_mode(client, callback_query):
    global MAINTENANCE_MODE
    MAINTENANCE_MODE = not MAINTENANCE_MODE  # Invert current mode

    await callback_query.answer("Maintenance mode is " + ("ON" if MAINTENANCE_MODE else "OFF"), show_alert=True)

    # Update reply markup according to the new mode
    markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Mode", callback_data="mode_info"),
                InlineKeyboardButton("ON" if MAINTENANCE_MODE else "OFF", callback_data="set_mode")
            ]
        ]
    )

    await callback_query.message.edit_reply_markup(reply_markup=markup)

@Client.on_callback_query(filters.regex(r"^mode_info$") & filters.user(ADMINS))
async def maintenance_mode_info(client, callback_query):
    await callback_query.answer(
        text="This feature allows you to enable maintenance mode for the bot. "
             "When enabled, users will receive a maintenance message if they send a message or command.",
        show_alert=True
    )


@Client.on_message(filters.command)
async def handle_maintenance(client, message):
    if MAINTENANCE_MODE and message.from_user.id not in ADMINS:
        await message.reply_text("Sorry, the bot is currently under maintenance. Please try again later.")
    else:
        return
@Client.on_message((filters.group | filters.private) & filters.text & filters.incoming)
async def handle_maintenance_private(bot, message):
    if MAINTENANCE_MODE and message.from_user.id not in ADMINS:
        await message.reply_text("Sorry, the bot is currently under maintenance. Please try again later.")
    else:
        return

