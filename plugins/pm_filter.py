import re
import ast
import math
import random
import asyncio
import logging
import datetime
from pytz import timezone

from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid

from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results, get_bad_files
from database.filters_mdb import del_all, find_filter, get_filters
from database.gfilters_mdb import find_gfilter, get_gfilters, del_allg
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, make_inactive

from Script import script
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink, send_all, check_verification, get_token

from info import (
    ADMINS,
    AUTH_CHANNEL,
    AUTH_USERS,
    SUPPORT_CHAT_ID,
    CUSTOM_FILE_CAPTION,
    MSG_ALRT,
    PICS,
    AUTH_GROUPS,
    P_TTI_SHOW_OFF,
    GRP_LNK,
    CHNL_LNK,
    NOR_IMG,
    LOG_CHANNEL,
    SPELL_IMG,
    MAX_B_TN,
    IMDB,
    SINGLE_BUTTON,
    SPELL_CHECK_REPLY,
    IMDB_TEMPLATE,
    NO_RESULTS_MSG,
    IS_VERIFY,
    HOW_TO_VERIFY
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}


@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if message.chat.id != SUPPORT_CHAT_ID:
        glob = await global_filters(client, message)
        if glob == False:
            manual = await manual_filters(client, message)
            if manual == False:
                settings = await get_settings(message.chat.id)
                try:
                    if settings['auto_ffilter']:
                        await auto_filter(client, message)
                except KeyError:
                    grpid = await active_connection(str(message.from_user.id))
                    await save_group_settings(grpid, 'auto_ffilter', True)
                    settings = await get_settings(message.chat.id)
                    if settings['auto_ffilter']:
                        await auto_filter(client, message)
    else:
        # A better logic to avoid repeated lines of code in the auto_filter function
        search = message.text
        temp_files, temp_offset, total_results = await get_search_results(chat_id=message.chat.id, query=search.lower(), offset=0, filter=True)
        if total_results == 0:
            return
        else:
            buttons = [
                [
                    InlineKeyboardButton("Official Group", url='https://t.me/+GEXyMerPdLpiMjBl')
                ]
            ]
            await message.reply_text(
                text=f"<b>Hello {message.from_user.mention}, {str(total_results)} results were found in my database for your query '{search}'. Please use inline search or create a group and add me as an admin to access movie files. This is a support group, so you can't get files from here...\n\nFor Movies, join</b>",
                reply_markup=markup,
                parse_mode=enums.ParseMode.HTML
            )
            
@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id

    # Set the timezone to India
    india_timezone = timezone('Asia/Kolkata')
    now = datetime.datetime.now(india_timezone)

    # Get the current time of day and date
    current_hour = now.hour
    time_suffix = "AM" if current_hour < 12 else "PM"
    formatted_time = now.strftime('%I:%M %p').lstrip('0')

    # Get the current date in Day-Month Name-Year format
    formatted_date = now.strftime('%d %B %Y')

    if 5 <= current_hour < 12:
        greeting = "Good morning ☀️"
    elif 12 <= current_hour < 18:
        greeting = "Good afternoon 🌤️"
    elif 18 <= current_hour < 22:
        greeting = "Good evening 🌇"
    else:
        greeting = "Good night 🌙"

    if content.startswith("/") or content.startswith("#"):
        return  # ignore commands and hashtags
    if user_id in ADMINS:
        return  # ignore admins

    # Get the total users count
    total_users = await db.total_users_count()

    reply_text = f"<b>{greeting} {user}!\n\nThanks For Choosing Us 🎉...\n\nJoin Our **𝙿𝚄𝙱𝙻𝙸𝙲 𝙶𝚁𝙾𝚄𝙿** For Sending Movie Names in Group Bot Reply Movies\n\nIf You Want Private Search Movies, Join Our **𝙿𝙼 𝚂𝙴𝙰𝚁𝙲𝙷** Bot to Send Movie Names. Bot Will Reply with Movies\n\nIf Any Bot Is Down, Check the Alternatives in **𝙼𝙾𝚁𝙴 𝙱𝙾𝚃𝚂** Official Channel</b>"

    # Create buttons for the reply message
    buttons = [
        [
            InlineKeyboardButton("𝙿𝚄𝙱𝙻𝙸𝙲 𝙶𝚁𝙾𝚄𝙿", url="https://t.me/MoviesHubBotGroup"),
            InlineKeyboardButton("𝙿𝙼 𝚂𝙴𝙰𝚁𝙲𝙷", url="https://t.me/iPepkornBot?start")
        ],
        [
            InlineKeyboardButton("𝙼𝙾𝚁𝙴 𝙱𝙾𝚃𝚂", url="https://t.me/iPepkornBots/8")
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # Set quote to True
    quote = True

    # Send the reply message with buttons
    await message.reply_text(
        text=reply_text,
        reply_markup=keyboard,
        quote=quote
    )

    # Send the log message to the specified channel with a button to send a message to the user
    log_buttons = [
        [
            InlineKeyboardButton("Send Message to User", callback_data=f"send_message:{user_id}")
        ]
    ]
    log_keyboard = InlineKeyboardMarkup(log_buttons)

    await bot.send_message(
        chat_id=LOG_CHANNEL,
        text=f"<b>#PM_MSG\n\nUser: {user}\nID: {user_id}\n\nMessage: {content}\n\nDate: {formatted_date}\nTime: {formatted_time}\nTotal Users: {total_users}</b>",
        reply_markup=log_keyboard,
    )
    
    
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        return

    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return

    settings = await get_settings(query.message.chat.id)
    temp.SEND_ALL_TEMP[query.from_user.id] = files

    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(query.message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False

    if ENABLE_SHORTLINK and settings['button']:
        btn = [
            [
                InlineKeyboardButton(text=f"[{get_size(file.file_size)}] {file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")),
            ]
            for file in files
        ]
    elif ENABLE_SHORTLINK and not settings['button']:
        btn = [
            [
                InlineKeyboardButton(text=f"{file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")),
                InlineKeyboardButton(text=f"{get_size(file.file_size)}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")),
            ]
            for file in files
        ]
    elif settings['button'] and not ENABLE_SHORTLINK:
        btn = [
            [
                InlineKeyboardButton(text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'files#{file.file_id}'),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'files#{file.file_id}'),
                InlineKeyboardButton(text=f"{get_size(file.file_size)}", callback_data=f'files_#{file.file_id}',),
            ]
            for file in files
        ]

    try:
        if settings['auto_delete']:
            btn.insert(0,
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
                    InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                ]
            )
        else:
            btn.insert(0,
                [
                    InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                ]
            )
    except KeyError:
        await save_group_settings(query.message.chat.id, 'auto_delete', True)
        btn.insert(0,
            [
                InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
                InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                InlineKeyboardButton(f'ꜱᴇʀɪᴇꜳ', 'sinfo')
            ]
        )

    try:
        if settings['max_btn']:
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append(
                    [
                        InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")
                    ]
                )
            elif off_set is None:
                btn.append(
                    [
                        InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                    ]
                )
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        else:
            if 0 < offset <= int(MAX_B_TN):
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - int(MAX_B_TN)
            if n_offset == 0:
                btn.append(
                    [
                        InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")
                    ]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                        InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
    except KeyError:
        await save_group_settings(query.message.chat.id, 'max_btn', True)
        if 0 < offset <= 10:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - 10
        if n_offset == 0:
            btn.append(
                [
                    InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                    InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")
            ]
        )
        elif off_set is None:
            btn.append([InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
        else:
            btn.append(
                [
                    InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                    InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                    InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                ],
            )

    btn.insert(0,
        [
            InlineKeyboardButton("! Sᴇɴᴅ Aʟʟ Tᴏ PM !", callback_data=f"send_fall#files#{offset}#{req}"),
            InlineKeyboardButton("! Lᴀɴɢᴜᴀɢᴇs !", callback_data=f"select_lang#{req}")
        ]
    )
    btn.insert(0,
        [
            InlineKeyboardButton("⚡ Cʜᴇᴄᴋ Bᴏᴛ PM ⚡", url=f"https://t.me/{temp.U_NAME}")
        ]
    )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()
                   
                   
@Client.on_callback_query(filters.regex(r"^lang"))
async def language_check(bot, query):
    _, userid, language = query.data.split("#")
    if int(userid) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if language == "unknown":
        return await query.answer("Sᴇʟᴇᴄᴛ ᴀɴʏ ʟᴀɴɢᴜᴀɢᴇ ғʀᴏᴍ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs !", show_alert=True)
    movie = temp.KEYWORD.get(query.from_user.id)
    if not movie:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if language != "home":
        movie = f"{movie} {language}"
    files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
    if files:
        settings = await get_settings(query.message.chat.id)
        temp.SEND_ALL_TEMP[query.from_user.id] = files
        if 'is_shortlink' in settings.keys():
            ENABLE_SHORTLINK = settings['is_shortlink']
        else:
            await save_group_settings(query.message.chat.id, 'is_shortlink', False)
            ENABLE_SHORTLINK = False
        pre = 'filep' if settings['file_secure'] else 'file'
        if ENABLE_SHORTLINK and settings['button']:
            btn = [
                [
                    InlineKeyboardButton(text=f"[{get_size(file.file_size)}] {file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")),
                ]
                for file in files
            ]
        elif ENABLE_SHORTLINK and not settings['button']:
            btn = [
                [
                    InlineKeyboardButton(text=f"{file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")),
                    InlineKeyboardButton(text=f"{get_size(file.file_size)}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")),
                ]
                for file in files
            ]
        elif settings['button'] and not ENABLE_SHORTLINK:
            btn = [
                [
                    InlineKeyboardButton(text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'{pre}#{file.file_id}'),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'{pre}#{file.file_id}',),
                    InlineKeyboardButton(text=f"{get_size(file.file_size)}", callback_data=f'{pre}#{file.file_id}',),
                ]
                for file in files
            ]

        try:
            if settings['auto_delete']:
                btn.insert(0, 
                    [
                        InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
                        InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                        InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                    ]
                )

            else:
                btn.insert(0, 
                    [
                        InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                        InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                    ]
                )
                    
        except KeyError:
            await save_group_settings(query.message.chat.id, 'auto_delete', True)
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
                    InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton(f'ꜱᴇʀɪᴇꜳ', 'sinfo')
                ]
            )
        
        btn.insert(0, 
            [
                InlineKeyboardButton("! Sᴇɴᴅ Aʟʟ Tᴏ PM !", callback_data=f"send_fall#{pre}#{0}#{userid}"),
                InlineKeyboardButton("! Lᴀɴɢᴜᴀɢᴇs !", callback_data=f"select_lang#{userid}")
            ]
        )

        btn.insert(0,
            [
                InlineKeyboardButton("⚡ Cʜᴇᴄᴋ Bᴏᴛ PM ⚡", url=f"https://t.me/{temp.U_NAME}")
            ]
        )

        if offset != "":
            key = f"{query.message.chat.id}-{query.message.id}"
            BUTTONS[key] = movie
            req = userid
            try:
                if settings['max_btn']:
                    btn.append(
                        [
                            InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), 
                            InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), 
                            InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")
                        ]
                    )

                else:
                    btn.append(
                        [
                            InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), 
                            InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), 
                            InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")
                        ]
                    )
            except KeyError:
                await save_group_settings(query.message.chat.id, 'max_btn', True)
                btn.append(
                    [
                        InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), 
                        InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), 
                        InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")
                    ]
                )
        else:
            btn.append(
                [
                    InlineKeyboardButton(text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄",callback_data="pages")
                ]
            )
        try:
            await query.edit_message_reply_markup(                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
        await query.answer()
    else:
        return await query.answer(f"Sᴏʀʀʏ, Nᴏ ғɪʟᴇs ғᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {movie}.", show_alert=True)


@Client.on_callback_query(filters.regex(r"^select_lang"))
async def select_language(bot, query):
    _, userid = query.data.split("#")
    if int(userid) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)

    btn = [
        [
            InlineKeyboardButton("Select Your Desired Language", callback_data=f"lang#{userid}#unknown")
        ],
        [
            InlineKeyboardButton("English", callback_data=f"lang#{userid}#eng"),
            InlineKeyboardButton("Tamil", callback_data=f"lang#{userid}#tam"),
            InlineKeyboardButton("Hindi", callback_data=f"lang#{userid}#hin")
        ],
        [
            InlineKeyboardButton("Kannada", callback_data=f"lang#{userid}#kan"),
            InlineKeyboardButton("Telugu", callback_data=f"lang#{userid}#tel"),
            InlineKeyboardButton("Marathi", callback_data=f"lang#{userid}#mar") 
        ],
        [
            InlineKeyboardButton("Malayalam", callback_data=f"lang#{userid}#mal"),
            InlineKeyboardButton("Tamil", callback_data=f"lang#{userid}#tam")
        ],
        [
            InlineKeyboardButton("Multi Audio", callback_data=f"lang#{userid}#multi"),
            InlineKeyboardButton("Dual Audio", callback_data=f"lang#{userid}#dual")
        ],
        [
            InlineKeyboardButton("Go Back", callback_data=f"lang#{userid}#home")
        ]
    ]

    try:
        # Edit the message reply markup with the new language selection buttons
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        # Handle the case where the message has not been modified
        pass

    await query.answer()
    
    
@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movie = movies[(int(movie_))]
    await query.answer(script.TOP_ALRT_MSG)
    gl = await global_filters(bot, query.message, text=movie)
    if gl == False:
        k = await manual_filters(bot, query.message, text=movie)
        if k == False:
            files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
            if files:
                k = (movie, files, offset, total_results)
                await auto_filter(bot, query, k)
            else:
                reqstr1 = query.from_user.id if query.from_user else 0
                reqstr = await bot.get_users(reqstr1)
                if NO_RESULTS_MSG:
                    await bot.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, movie)))
                k = await query.message.edit(script.MVE_NT_FND)
                await asyncio.sleep(10)
                await k.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()

    elif query.data == "gfiltersdeleteallconfirm":
        await del_allg(query.message, 'gfilters')
        await query.answer("Done!")
        return

    elif query.data == "gfiltersdeleteallcancel": 
        await query.message.reply_to_message.delete()
        await query.message.delete()
        await query.answer("Process Cancelled!")
        return

    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            # Handle private chat
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!", quote=True)
                    return await query.answer(MSG_ALRT)
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups.",
                    quote=True
                )
                return await query.answer(MSG_ALRT)

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            # Handle group or supergroup chat
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer(MSG_ALRT)

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Authorized User to do that!", show_alert=True)

    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type
    
        if chat_type == enums.ChatType.PRIVATE:
            # Handle private chat
            await query.message.reply_to_message.delete()
            await query.message.delete()
    
        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            # Handle group or supergroup chat
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("That's not for you!!", show_alert=True)    

    elif "groupcb" in query.data:
        await query.answer()
    
        group_id = query.data.split(":")[1]
    
        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id
    
        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"
    
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
                    InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")
                ],
                [
                    InlineKeyboardButton("BACK", callback_data="backcb")
                ]
            ]
        )    
        await query.message.edit_text(
            f"Group Name: **{title}**\nGroup ID: `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer(MSG_ALRT)

    elif "connectcb" in query.data:
        await query.answer()    
        group_id = query.data.split(":")[1]    
        hr = await client.get_chat(int(group_id))    
        title = hr.title
        user_id = query.from_user.id
        mkact = await make_active(str(user_id), str(group_id))
        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer(MSG_ALRT)

    elif "disconnect" in query.data:
        await query.answer()
    
        group_id = query.data.split(":")[1]
    
        hr = await client.get_chat(int(group_id))
    
        title = hr.title
        user_id = query.from_user.id
    
        mkinact = await make_inactive(str(user_id))
    
        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)

    elif "deletecb" in query.data:
        await query.answer()
        user_id = query.from_user.id
        group_id = query.data.split(":")[1]    
        delcon = await delete_connection(str(user_id), str(group_id))
        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection!"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)    

    elif query.data == "backcb":
        await query.answer()
    
        user_id = query.from_user.id
    
        group_ids = await all_connections(str(user_id))
        if group_ids is None:
            await query.message.edit_text(
                "There are no active connections! Connect to some groups first."
            )
            return await query.answer(MSG_ALRT)
    
        buttons = []
        for group_id in group_ids:
            try:
                ttl = await client.get_chat(int(group_id))
                title = ttl.title
                active = await if_active(str(user_id), str(group_id))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(text=f"{title}{act}", callback_data=f"groupcb:{group_id}:{act}")
                    ]
                )
            except:
                pass
    
        if buttons:
            await query.message.edit_text(
                "Your connected group details:\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    elif "gfilteralert" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_gfilter('gfilters', keyword)
        
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)   

    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)    

    if query.data.startswith("file"):
        clicked = query.from_user.id
        try:
            typed = query.message.reply_to_message.from_user.id
        except:
            typed = query.from_user.id
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        
        if not files_:
            return await query.answer('No such file exists.')
        
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        
        if f_caption is None:
            f_caption = f"{files.file_name}"
    
        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                if clicked == typed:
                    await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                else:
                    await query.answer(f"Hey {query.from_user.first_name}, This Is Not Your Movie Request. Request Yours!", show_alert=True)
            elif settings['botpm']:
                if clicked == typed:
                    await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                else:
                    await query.answer(f"Hey {query.from_user.first_name}, This Is Not Your Movie Request. Request Yours!", show_alert=True)
            else:
                if clicked == typed:
                    if IS_VERIFY and not await check_verification(client, query.from_user.id):
                        btn = [
                            [
                                InlineKeyboardButton("Verify", url=await get_token(client, query.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
                                InlineKeyboardButton("How To Verify", url=HOW_TO_VERIFY)
                            ]
                        ]
                        await client.send_message(
                            chat_id=query.from_user.id,
                            text="<b>You are not verified!\nKindly verify to continue so that you can get access to unlimited movies until 12 hours from now!</b>",
                            protect_content=True if ident == 'checksubp' else False,
                            disable_web_page_preview=True,
                            parse_mode=enums.ParseMode.HTML,
                            reply_markup=InlineKeyboardMarkup(btn)
                        )
                        return await query.answer("Hey, You have not verified today. You have to verify to continue. Check my PM to verify and get files!", show_alert=True)
                    else:
                        await client.send_cached_media(
                            chat_id=query.from_user.id,
                            file_id=file_id,
                            caption=f_caption,
                            protect_content=True if ident == "filep" else False,
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [
                                        InlineKeyboardButton('Support Group', url=GRP_LNK),
                                        InlineKeyboardButton('Updates Channel', url=CHNL_LNK)
                                    ]                            
                                ]
                            )
                        )
                        return await query.answer('Check PM, I have sent files in PM', show_alert=True)
                else:
                    return await query.answer(f"Hey {query.from_user.first_name}, This Is Not Your Movie Request. Request Yours!", show_alert=True)
        except UserIsBlocked:
            await query.answer('Unblock the bot, mate!', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")    

    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("Join our backup channel, please! 😒", show_alert=True)
            return
        
        ident, file_id = query.data.split("#")
        
        if file_id == "send_all":
            send_files = temp.SEND_ALL_TEMP.get(query.from_user.id)
            is_over = await send_all(client, query.from_user.id, send_files, ident)
            
            if is_over == 'done':
                return await query.answer(f"Hey {query.from_user.first_name}, All files on this page have been sent successfully to your PM!", show_alert=True)
            elif is_over == 'fsub':
                return await query.answer("Hey, You are not joined in my backup channel. Check my PM to join and get files!", show_alert=True)
            elif is_over == 'verify':
                return await query.answer("Hey, You have not verified today. You have to verify to continue. Check my PM to verify and get files!", show_alert=True)
            else:
                return await query.answer(f"Error: {is_over}", show_alert=True)
        
        files_ = await get_file_details(file_id)
        
        if not files_:
            return await query.answer('No such file exists.')
        
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        
        if f_caption is None:
            f_caption = f"{title}"
        
        await query.answer()
        
        if IS_VERIFY and not await check_verification(client, query.from_user.id):
            btn = [
                [
                    InlineKeyboardButton("Verify", url=await get_token(client, query.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
                    InlineKeyboardButton("How To Verify", url=HOW_TO_VERIFY)
                ]
            ]
            
            await client.send_message(
                chat_id=query.from_user.id,
                text="<b>You are not verified!\nKindly verify to continue so that you can get access to unlimited movies until 12 hours from now!</b>",
                protect_content=True if ident == 'checksubp' else False,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            return
        
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton('Support Group', url=GRP_LNK),
                        InlineKeyboardButton('Updates Channel', url=CHNL_LNK)
                    ]
                ]
            )
        )        

    elif query.data == "pages":
        await query.answer()

    elif query.data.startswith("send_fall"):
        temp_var, ident, offset, userid = query.data.split("#")
        
        if int(userid) not in [query.from_user.id, 0]:
            return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        
        files = temp.SEND_ALL_TEMP.get(query.from_user.id)
        is_over = await send_all(client, query.from_user.id, files, ident)
        
        if is_over == 'done':
            return await query.answer(f"Hey {query.from_user.first_name}, All files on this page have been sent successfully to your PM!", show_alert=True)
        elif is_over == 'fsub':
            return await query.answer("Hey, You are not joined in my backup channel. Check my PM to join and get files!", show_alert=True)
        elif is_over == 'verify':
            return await query.answer("Hey, You have not verified today. You have to verify to continue. Check my PM to verify and get files!", show_alert=True)
        else:
            return await query.answer(f"Error: {is_over}", show_alert=True)
    
    elif query.data.startswith("killfilesdq"):
        ident, keyword = query.data.split("#")
        
        await query.message.edit_text(f"<b>Fetching Files for your query {keyword} on DB... Please wait...</b>")
        
        files, total = await get_bad_files(keyword)
        
        await query.message.edit_text(f"<b>Found {total} Files for your query {keyword}!\n\nFile deletion process will start in 5 seconds!</b>")
        
        await asyncio.sleep(5)
        deleted = 0
        
        async with lock:
            try:
                for file in files:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media.collection.delete_one({
                        '_id': file_ids,
                    })
                    
                    if result.deleted_count:
                        logger.info(f'File Found for your query {keyword}! Successfully deleted {file_name} from database.')
                    
                    deleted += 1
                    
                    if deleted % 20 == 0:
                        await query.message.edit_text(f"<b>Process started for deleting files from DB. Successfully deleted {str(deleted)} files from DB for your query {keyword}!\n\nPlease wait...</b>")
            except Exception as e:
                logger.exception(e)
                await query.message.edit_text(f'Error: {e}')
            else:
                await query.message.edit_text(f"<b>Process Completed for file deletion!\n\nSuccessfully deleted {str(deleted)} files from DB for your query {keyword}.</b>")    

    elif query.data.startswith("opnsetgrp"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
    
        if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
        ):
            await query.answer("You don't have the rights to do this!", show_alert=True)
            return
    
        title = query.message.chat.title
        settings = await get_settings(grp_id)
    
        if settings is not None:
            if userid in ADMINS:
                buttons = [
                    [
                        InlineKeyboardButton('Filter Button', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                        InlineKeyboardButton('Single' if settings["button"] else 'Double', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('File Send Mode', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                        InlineKeyboardButton('Manual Start' if settings["botpm"] else 'Auto Send', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Protect Content', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["file_secure"] else '✘ Off', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["imdb"] else '✘ Off', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Spell Check', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["spell_check"] else '✘ Off', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Welcome Msg', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["welcome"] else '✘ Off', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Auto-Delete', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                        InlineKeyboardButton('10 Mins' if settings["auto_delete"] else '✘ Off', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Auto-Filter', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["auto_ffilter"] else '✘ Off', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Max Buttons', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                        InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('ShortLink', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["is_shortlink"] else '✘ Off', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                    ]
                ]
            else:
                buttons = [
                    [
                        InlineKeyboardButton('Filter Button', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                        InlineKeyboardButton('Single' if settings["button"] else 'Double', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Protect Content', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["file_secure"] else '✘ Off', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["imdb"] else '✘ Off', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Spell Check', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["spell_check"] else '✘ Off', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Welcome Msg', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["welcome"] else '✘ Off', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Auto-Delete', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                        InlineKeyboardButton('10 Mins' if settings["auto_delete"] else '✘ Off', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Auto-Filter', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["auto_ffilter"] else '✘ Off', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Max Buttons', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                        InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('ShortLink', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["is_shortlink"] else '✘ Off', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(buttons)
        
                await query.message.edit_text(
                    text=f"<b>Change Your Settings for {title} As You Wish ⚙</b>",
                    disable_web_page_preview=True,
                    parse_mode=enums.ParseMode.HTML
                )
    
            await query.message.edit_reply_markup(reply_markup)    

    elif query.data.startswith("opnsetpm"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        
        if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
        ):
            await query.answer("Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Tʜᴇ Rɪɢʜᴛs Tᴏ Dᴏ Tʜɪs !", show_alert=True)
            return
        
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        btn2 = [
            [
                InlineKeyboardButton("Cʜᴇᴄᴋ PM", url=f"t.me/{temp.U_NAME}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(btn2)
        
        await query.message.edit_text(f"<b>Yᴏᴜʀ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ ғᴏʀ {title} ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ʏᴏᴜʀ PM</b>")
        await query.message.edit_reply_markup(reply_markup)
        
        if settings is not None:
            if userid in ADMINS:
                buttons = [
                    [
                        InlineKeyboardButton('Fɪʟᴛᴇʀ Bᴜᴛᴛᴏɴ', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                        InlineKeyboardButton('Sɪɴɢʟᴇ' if settings["button"] else 'Dᴏᴜʙʟᴇ', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Fɪʟᴇ Sᴇɴᴅ Mᴏᴅᴇ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                        InlineKeyboardButton('Mᴀɴᴜᴀʟ Sᴛᴀʀᴛ' if settings["botpm"] else 'Aᴜᴛᴏ Sᴇɴᴅ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ Oɴ' if settings["file_secure"] else '✘ Oғғ', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                        InlineKeyboardButton('10 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Aᴜᴛᴏ-Fɪʟᴛᴇʀ', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                        InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('SʜᴏʀᴛLɪɴᴋ', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                    ]
                ]
            else:
                buttons = [
                    [
                        InlineKeyboardButton('Fɪʟᴛᴇʀ Bᴜᴛᴛᴏɴ', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                        InlineKeyboardButton('Sɪɴɢʟᴇ' if settings["button"] else 'Dᴏᴜʙʟᴇ', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ Oɴ' if settings["file_secure"] else '✘ Oғғ', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                        InlineKeyboardButton('10 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Aᴜᴛᴏ-Fɪʟᴛᴇʀ', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                        InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('SʜᴏʀᴛLɪɴᴋ', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(buttons)
                
                await client.send_message(
                    chat_id=userid,
                    text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                    parse_mode=enums.ParseMode.HTML,
                    reply_to_message_id=query.message.id
                )

    elif query.data.startswith("show_option"):
            ident, from_user = query.data.split("#")
            btn = [
                [
                    InlineKeyboardButton("Unavailable", callback_data=f"unavailable#{from_user}"),
                    InlineKeyboardButton("Uploaded", callback_data=f"uploaded#{from_user}")
                ],
                [
                    InlineKeyboardButton("Already Available", callback_data=f"already_available#{from_user}")
                ]
            ]
            btn2 = [
                [
                    InlineKeyboardButton("View Status", url=f"{query.message.link}")
                ]
            ]
            if query.from_user.id in ADMINS:
                user = await client.get_users(from_user)
                reply_markup = InlineKeyboardMarkup(btn)
                await query.message.edit_reply_markup(reply_markup)
                await query.answer("Here are the options!")
            else:
                await query.answer("You don't have sufficient rights to do this!", show_alert=True)    

    elif query.data.startswith("unavailable"):
        ident, from_user = query.data.split("#")
        btn = [
            [
                InlineKeyboardButton("⚠️ Unavailable ⚠️", callback_data=f"unalert#{from_user}")
            ]
        ]
        btn2 = [
            [
                InlineKeyboardButton("View Status", url=f"{query.message.link}")
            ]
        ]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Set to Unavailable!")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<b>Hey {user.mention}, Sorry, your request is unavailable. So our moderators can't upload it.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hey {user.mention}, Sorry, your request is unavailable. So our moderators can't upload it.\n\nNote: This message is sent to this group because you've blocked the bot. To send this message to your PM, you must unblock the bot.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("You don't have sufficient rights to do this!", show_alert=True)    

    elif query.data.startswith("uploaded"):
        ident, from_user = query.data.split("#")
        btn = [
            [
                InlineKeyboardButton("✅ Uploaded ✅", callback_data=f"upalert#{from_user}")
            ]
        ]
        btn2 = [
            [
                InlineKeyboardButton("View Status", url=f"{query.message.link}")
            ]
        ]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Set to Uploaded!")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<b>Hey {user.mention}, Your request has been uploaded by our moderators. Kindly search again.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hey {user.mention}, Your request has been uploaded by our moderators. Kindly search again.\n\nNote: This message is sent to this group because you've blocked the bot. To send this message to your PM, you must unblock the bot.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("You don't have sufficient rights to do this!", show_alert=True)

    elif query.data.startswith("already_available"):
        ident, from_user = query.data.split("#")
        btn = [
            [
                InlineKeyboardButton("🟢 Already Available 🟢", callback_data=f"alalert#{from_user}")
            ]
        ]
        btn2 = [
            [
                InlineKeyboardButton("View Status", url=f"{query.message.link}")
            ]
        ]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Set to Already Available!")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<b>Hey {user.mention}, Your request is already available on our bot's database. Kindly search again.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hey {user.mention}, Your request is already available on our bot's database. Kindly search again.\n\nNote: This message is sent to this group because you've blocked the bot. To send this message to your PM, you must unblock the bot.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("You don't have sufficient rights to do this!", show_alert=True)    

    elif query.data.startswith("alalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hey {user.first_name}, Your request is already available!", show_alert=True)
        else:
            await query.answer("You don't have sufficient rights to do this!", show_alert=True)    

    elif query.data.startswith("upalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hey {user.first_name}, Your request has been uploaded!", show_alert=True)
        else:
            await query.answer("You don't have sufficient rights to do this!", show_alert=True)    

    elif query.data.startswith("unalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hey {user.first_name}, Your request is unavailable!", show_alert=True)
        else:
            await query.answer("You don't have sufficient rights to do this!", show_alert=True)

    elif query.data == "reqinfo":
        await query.answer(text=script.REQINFO, show_alert=True)

    elif query.data == "minfo":
        await query.answer(text=script.MINFO, show_alert=True)

    elif query.data == "sinfo":
        await query.answer(text=script.SINFO, show_alert=True)

    elif query.data == "start":
        buttons = [
            [
                InlineKeyboardButton("➕️ Add Me to Your Chat ➕", url=f"http://t.me/{temp.U_NAME}?startgroup=true")
            ],
            [
                InlineKeyboardButton("🔍 Search", switch_inline_query_current_chat=''),
                InlineKeyboardButton("📢 Channel", url=UPDATE_CHANNEL)
            ],
            [
                InlineKeyboardButton("ℹ️ Help", callback_data="help"),
                InlineKeyboardButton("📚 About", callback_data="about")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer(MSG_ALRT)
        
    elif query.data == "filters":
        buttons = [
            [
                InlineKeyboardButton('Auto Filter', callback_data='autofilter'),
                InlineKeyboardButton('Manual Filter', callback_data='manuelfilter')
            ],
            [
                InlineKeyboardButton('Global Filters', callback_data='global_filters'),
                InlineKeyboardButton('Back', callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS)
        ))
        await query.message.edit_text(
            text=script.ALL_FILTERS.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "global_filters":
        buttons = [
            [
                InlineKeyboardButton('Home', callback_data='start')
            ],
            [
                InlineKeyboardButton('Back', callback_data='filters')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS)
        ))
        await query.message.edit_text(
            text=script.GFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "help":
        buttons = [
            [
                InlineKeyboardButton('Filters', callback_data='filters'),
                InlineKeyboardButton('File Store', callback_data='store_file')
            ],
            [
                InlineKeyboardButton('Connection', callback_data='coct'),
                InlineKeyboardButton('Extra Mods', callback_data='extra')
            ],
            [
                InlineKeyboardButton('Home', callback_data='start'),
                InlineKeyboardButton('Status', callback_data='stats')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS)
        ))
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "about":
        buttons = [
            [
                InlineKeyboardButton('Support Group', url=GRP_LNK),
                InlineKeyboardButton('Source Code', callback_data='source')
            ],
            [
                InlineKeyboardButton('More Bots', url=MORE_LNK),
                InlineKeyboardButton('Status', callback_data='stats')
            ],
            [
                InlineKeyboardButton('Home', callback_data='start'),
                InlineKeyboardButton('Close', callback_data='close_data')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS)
        ))
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "source":
        buttons = [
            [
                InlineKeyboardButton('Home', callback_data='start')
            ],
            [
                InlineKeyboardButton('Back', callback_data='about')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS)
        ))
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "manuelfilter":
        buttons = [
            [
                InlineKeyboardButton('Buttons', callback_data='button'),
                InlineKeyboardButton('Back', callback_data='filters')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS)
        ))
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "button":
        buttons = [
            [
                InlineKeyboardButton('Home', callback_data='start')
            ],
            [
                InlineKeyboardButton('Back', callback_data='manuelfilter')
            ]
        ]    
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS)
        ))
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "autofilter":
        buttons = [
            [
                InlineKeyboardButton('Home', callback_data='start')
            ],
            [
                InlineKeyboardButton('Back', callback_data='filters')
            ]
        ]        
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS)
        ))
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "coct":
        buttons = [
            [
                InlineKeyboardButton('Home', callback_data='start'),
                InlineKeyboardButton('Back', callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS)
        ))
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "extra":
        buttons = [
            [
                InlineKeyboardButton('Admin', callback_data='admin'),
                InlineKeyboardButton('Back', callback_data='help')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS)
        ))
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "store_file":
        buttons = [
            [
                InlineKeyboardButton('Home', callback_data='start'),
                InlineKeyboardButton('Back', callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS)
        ))
        await query.message.edit_text(
            text=script.FILE_STORE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "admin":
        buttons = [
            [
                InlineKeyboardButton('Home', callback_data='start'),
                InlineKeyboardButton('Back', callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS)
        ))
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "stats":
        buttons = [
            [
                InlineKeyboardButton('Refresh', callback_data='rfrsh'),
                InlineKeyboardButton('Back', callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS)
        ))
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDB Database")
        buttons = [
            [
                InlineKeyboardButton('Refresh', callback_data='rfrsh'),
                InlineKeyboardButton('Back', callback_data='help')
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS)
        ))
        reply_markup = InlineKeyboardMarkup(buttons)        
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)        
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "owner_info":
        btn = [
            [
                InlineKeyboardButton("Back", callback_data="start"),
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS)
        ))
        reply_markup = InlineKeyboardMarkup(btn)
        await query.message.edit_text(
            text=script.OWNER_INFO,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))
    
        if set_type == 'is_shortlink' and query.from_user.id not in ADMINS:
            return await query.answer(text=f"Hey {query.from_user.first_name}, you can't change shortlink settings for your group!\n\nIt's an admin-only setting!", show_alert=True)
    
        if str(grp_id) != str(grpid) and query.from_user.id not in ADMINS:
            await query.message.edit("Your active connection has been changed. Go to /connections and change your active connection.")
            return await query.answer(MSG_ALRT)
    
        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)
    
        settings = await get_settings(grpid)
    
        if settings is not None:
            if query.from_user.id in ADMINS:
                buttons = [
                    [
                        InlineKeyboardButton('Filter Button', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                        InlineKeyboardButton('Single' if settings["button"] else 'Double', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('File Send Mode', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                        InlineKeyboardButton('Manual Start' if settings["botpm"] else 'Auto Send', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Protect Content', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["file_secure"] else '✘ Off', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('IMDb', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["imdb"] else '✘ Off', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Spell Check', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["spell_check"] else '✘ Off', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Welcome Msg', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["welcome"] else '✘ Off', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Auto-Delete', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                        InlineKeyboardButton('10 Mins' if settings["auto_delete"] else '✘ Off', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Auto-Filter', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["auto_ffilter"] else '✘ Off', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Max Buttons', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                        InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_BTN}', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Shortlink', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["is_shortlink"] else '✘ Off', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                    ]
                ]
            else:
                buttons = [
                    [
                        InlineKeyboardButton('Filter Button', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                        InlineKeyboardButton('Single' if settings["button"] else 'Double', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Protect Content', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["file_secure"] else '✘ Off', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('IMDb', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["imdb"] else '✘ Off', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Spell Check', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["spell_check"] else '✘ Off', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Welcome Msg', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["welcome"] else '✘ Off', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Auto-Delete', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                        InlineKeyboardButton('10 Mins' if settings["auto_delete"] else '✘ Off', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Auto-Filter', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["auto_ffilter"] else '✘ Off', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Max Buttons', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                        InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_BTN}', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Shortlink', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✔ On' if settings["is_shortlink"] else '✘ Off', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(buttons)
                await query.message.edit_reply_markup(reply_markup)
        
        await query.answer(MSG_ALRT)


async def auto_filter(client, msg, spoll=False):
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"):
            return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(message.chat.id, search.lower(), offset=0, filter=True)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_chok(client, msg)
                else:
                    if NO_RESULTS_MSG:
                        await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, search)))
                    return
        else:
            return
    else:
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
        settings = await get_settings(message.chat.id)

    temp.SEND_ALL_TEMP[message.from_user.id] = files
    temp.KEYWORD[message.from_user.id] = search

    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False

    pre = 'filep' if settings['file_secure'] else 'file'

    if ENABLE_SHORTLINK and settings["button"]:
        btn = [
            [
                InlineKeyboardButton(text=f"[{get_size(file.file_size)}] {file.file_name}", url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")),
            ]
            for file in files
        ]
    elif ENABLE_SHORTLINK and not settings["button"]:
        btn = [
            [
                InlineKeyboardButton(text=f"{file.file_name}", url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")),
                InlineKeyboardButton(text=f"{get_size(file.file_size)}", url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")),
            ]
            for file in files
        ]
    elif settings["button"] and not ENABLE_SHORTLINK:
        btn = [
            [
                InlineKeyboardButton(text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'{pre}#{file.file_id}'),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'{pre}#{file.file_id}',),
                InlineKeyboardButton(text=f"{get_size(file.file_size)}", callback_data=f'{pre}#{file.file_id}',),
            ]
            for file in files
        ]

    try:
        if settings['auto_delete']:
            btn.insert(0,
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
                    InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                ]
            )
        else:
            btn.insert(0,
                [
                    InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                ]
            )
    except KeyError:
        await save_group_settings(message.chat.id, 'auto_delete', True)
        btn.insert(0,
            [
                InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
                InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
            ]
        )

    btn.insert(0,
        [
            InlineKeyboardButton("! Sᴇɴᴅ Aʟʟ Tᴏ PM !", callback_data=f"send_fall#{pre}#{0}#{message.from_user.id}"),
            InlineKeyboardButton("! Lᴀɴɢᴜᴀɢᴇs !", callback_data=f"select_lang#{message.from_user.id}")
        ]
    )

    btn.insert(0,
        [
            InlineKeyboardButton("⚡ Cʜᴇᴄᴋ Bᴏᴛ PM ⚡", url=f"https://t.me/{temp.U_NAME}")
        ]
    )

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0

        try:
            if settings['max_btn']:
                btn.append(
                    [
                        InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"),
                        InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}", callback_data="pages"),
                        InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{offset}")
                    ]
                )
            else:
                btn.append(
                    [
                        InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"),
                        InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}", callback_data="pages"),
                        InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{offset}")
                    ]
                )
        except KeyError:
            await save_group_settings(message.chat.id, 'max_btn', True)
            btn.append(
                [
                    InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"),
                    InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}", callback_data="pages"),
                    InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{offset}")
                ]
            )
    else:
        btn.append(
            [
                InlineKeyboardButton(text="𝐍𝐎 𝑀𝑂𝑅𝐸 𝑃𝐴𝐺𝐸𝑆 𝐴𝑉𝐴𝐼𝐿𝐴𝐵𝐿𝐸", callback_data="pages")
            ]
        )

    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']

    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"<b>Hᴇʏ {message.from_user.mention}, Hᴇʀᴇ ɪs Wʜᴀᴛ I Fᴏᴜɴᴅ Iɴ Mʏ Dᴀᴛᴀʙᴀsᴇ Fᴏʀ Yᴏᴜʀ Qᴜᴇʀʏ {search}.</b>"

    if imdb and imdb.get('poster'):
        try:
            hehe = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(600)
                    await hehe.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(600)
                await hehe.delete()
                await message.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            hmm = await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(600)
                    await hmm.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(600)
                await hmm.delete()
                await message.delete()
        except Exception as e:
            logger.exception(e)
            fek = await message.reply_photo(photo=NOR_IMG, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(600)
                    await fek.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(600)
                await fek.delete()
                await message.delete()
    else:
        fuk = await message.reply_photo(photo=NOR_IMG, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
        try:
            if settings['auto_delete']:
                await asyncio.sleep(600)
                await fuk.delete()
                await message.delete()
        except KeyError:
            await save_group_settings(message.chat.id, 'auto_delete', True)
            await asyncio.sleep(600)
            await fuk.delete()
            await message.delete()

    if spoll:
        await msg.message.delete()


async def advantage_spell_chok(client, msg):
    mv_id = msg.id
    mv_rqst = msg.text
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    settings = await get_settings(msg.chat.id)
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # Please contribute some common words
    query = query.strip() + " movie"
    try:
        movies = await get_poster(mv_rqst, bulk=True)
    except Exception as e:
        logger.exception(e)
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [
            [
                InlineKeyboardButton("Google", url=f"https://www.google.com/search?q={reqst_gle}")
            ]
        ]
        if NO_RESULTS_MSG:
            await client.send_message(chat_id=LOG_CHANNEL, text=(script.NO_RESULTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await msg.reply_photo(
            photo=SPELL_IMG,
            caption=script.I_COULDNT_FIND.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(button)
        )
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist = []
    if not movies:
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [
            [
                InlineKeyboardButton("Google", url=f"https://www.google.com/search?q={reqst_gle}")
            ]
        ]
        if NO_RESULTS_MSG:
            await client.send_message(chat_id=LOG_CHANNEL, text=(script.NO_RESULTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await msg.reply_photo(
            photo=SPELL_IMG,
            caption=script.I_COULDNT_FIND.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(button)
        )
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist += [movie.get('title') for movie in movies]
    movielist += [f"{movie.get('title')} {movie.get('year')}" for movie in movies]
    SPELL_CHECK[mv_id] = movielist
    btn = [
        [
            InlineKeyboardButton(text=movie_name.strip(),callback_data=f"spol#{reqstr1}#{k}",)
        ]
        for k, movie_name in enumerate(movielist)
    ]
    btn.append(
        [
            InlineKeyboardButton(text="Close", callback_data=f'spol#{reqstr1}#close_spellcheck')
        ]
    )
    spell_check_del = await msg.reply_photo(
        photo=(SPELL_IMG),
        caption=(script.COULDNT_FIND.format(mv_rqst)),
        reply_markup=InlineKeyboardMarkup(btn)
    )
    try:
        if settings['auto_delete']:
            await asyncio.sleep(600)
            await spell_check_del.delete()
    except KeyError:
        grpid = await active_connection(str(msg.from_user.id))
        await save_group_settings(grpid, 'auto_delete', True)
        settings = await get_settings(msg.chat.id)
        if settings['auto_delete']:
            await asyncio.sleep(600)
            await spell_check_del.delete()


async def manual_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                        else:
                            button = eval(btn)
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                    elif btn == "[]":
                        joelkb = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            protect_content=True if settings["file_secure"] else False,
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                    else:
                        button = eval(btn)
                        joelkb = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False


async def global_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters('gfilters')
    
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                            manual = await manual_filters(client, message)
                            if manual == False:
                                settings = await get_settings(message.chat.id)
                                try:
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message)
                                        try:
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                    else:
                                        try:
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_ffilter', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message) 
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            
                        else:
                            button = eval(btn)
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                            manual = await manual_filters(client, message)
                            if manual == False:
                                settings = await get_settings(message.chat.id)
                                try:
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message)
                                        try:
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                    else:
                                        try:
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_ffilter', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message) 
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()

                    elif btn == "[]":
                        joelkb = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                        manual = await manual_filters(client, message)
                        if manual == False:
                            settings = await get_settings(message.chat.id)
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message) 
                        else:
                            try:
                                if settings['auto_delete']:
                                    await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await joelkb.delete()

                    else:
                        button = eval(btn)
                        joelkb = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        manual = await manual_filters(client, message)
                        if manual == False:
                            settings = await get_settings(message.chat.id)
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message) 
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
