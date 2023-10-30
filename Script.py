class script(object):
    START_TEXT = """<b>Hello {},
My Name Is <a href=https://t.me/{}>{}</a>, I Can Provide Movies, Just Add Me To Your Group And Enjoy 😍</b>"""

    HELP_TEXT = """<b>Hey {}
Here Is The Help For My Commands.</b>"""

    ABOUT_TEXT = """<b>✯ My Name: {}
✯ Creator: <a href='https://t.me/+UQSz8l_tSqc3MjJl'>iPapkorn Bots</a>
✯ Library: <a href='https://docs.pyrogram.org/'>Pyrogram</a>
✯ Language: <a href='https://www.python.org/download/releases/3.0/'>Python 3</a>
✯ Database: <a href='https://www.mongodb.com/'>MongoDB</a>
✯ Bot Server: <a href='https://app.koyeb.com/'>Koyeb</a>
✯ Build Status: v1.0.0</b>"""

    SOURCE_TEXT = """<b>Note:
- This bot is not an open-source project.
- Source - <a href='https://t.me/+UQSz8l_tSqc3MjJl'>More Bots</a>"""

    ALL_FILTERS = """
<b>Hey {}, These are my three types of filters.</b>"""

    AUTOFILTER_TXT = """Help: <b>Auto Filter</b>
<b>Note: File Index</b>
1. Make me the admin of your channel if it's private.
2. Ensure that your channel doesn't contain scams, porn, and fake files.
3. Forward the last message to me with quotes. I'll add all the files in that channel to my database.

<b>Note: AutoFilter</b>
1. Add the bot as an admin in your group.
2. Use /connect and connect your group to the bot.
3. Use /settings on the bot's PM and turn on AutoFilter in the settings menu."""

    MANUELFILTER_TXT = """Help: <b>Filters</b>
- Filters are a feature where users can set automated replies for a particular keyword, and I will respond whenever that keyword is found in the message.
<b>Note:</b>
1. This bot should have admin privileges.
2. Only admins can add filters in a chat.
3. Alert buttons have a limit of 64 characters.
Commands and Usage:
• /filter - <code>Add a filter in a chat</code>
• /filters - <code>List all the filters of a chat</code>
• /del - <code>Delete a specific filter in a chat</code>
• /delall - <code>Delete the whole filters in a chat (chat owner only)</code>"""

    GFILTER_TXT = """
<b>Welcome to Global Filters. Global Filters are the filters set by bot admins which will work on all groups.</b>

Available commands:
• /gfilter - <code>To create a global filter.</code>
• /gfilters - <code>To view all global filters.</code>
• /delg - <code>To delete a particular global filter.</code>
• /delallg - <code>To delete all global filters.</code>"""

    BUTTON_TXT = """Help: <b>Buttons</b>
- This bot supports both URL and alert inline buttons.
<b>Note:</b>
1. Telegram will not allow you to send buttons without any content, so content is mandatory.
2. This bot supports buttons with any Telegram media type.
3. Buttons should be properly parsed as Markdown format.
<b>URL Buttons:</b>
<code>[Button Text](buttonurl:https://t.me/Example)</code>
<b>Alert Buttons:</b>
<code>[Button Text](buttonalert:This is an alert message)</code>"""

    CONNECTION_TXT = """Help: <b>Connections</b>
- Used to connect the bot to PM for managing filters.
- It helps to avoid spamming in groups.
<b>Note:</b>
1. Only admins can add a connection.
2. Send <code>/connect</code> for connecting me to your PM.
Commands and Usage:
• /connect - <code>Connect a particular chat to your PM</code>
• /disconnect - <code>Disconnect from a chat</code>
• /connections - <code>List all your connections</code>"""

    EXTRAMOD_TXT = """Help: Extra Modules
<b>Note:</b>
These are the extra features of this bot.
Commands and Usage:
• /id - <code>Get ID of a specified user.</code>
• /info - <code>Get information about a user.</code>
• /imdb - <code>Get the film information from IMDb source.</code>
• /search - <code>Get the film information from various sources.</code>"""

    ADMIN_TXT = """Help: Admin Mods
<b>Note:</b>
This Module Only Works for My Admins
Commands and Usage:
• /logs - <code>To get the recent errors</code>
• /stats - <code>To get the status of files in the DB. [This Command Can Be Used by Anyone]</code>
• /delete - <code>To delete a specific file from the DB.</code>
• /users - <code>To get a list of my users and IDs.</code>
• /chats - <code>To get a list of my chats and IDs</code>
• /leave - <code>To leave from a chat.</code>
• /disable - <code>To disable a chat.</code>
• /ban - <code>To ban a user.</code>
• /unban - <code>To unban a user.</code>
• /channel - <code>To get a list of total connected channels</code>
• /broadcast - <code>To broadcast a message to all users</code>
• /grp_broadcast - <code>To broadcast a message to all connected groups.</code>
• /gfilter - <code>To add global filters</code>
• /gfilters - <code>To view a list of all global filters</code>
• /delg - <code>To delete a specific global filter</code>
• /request - <code>To send a Movie/Series request to bot admins. Only works on support group. [This Command Can Be Used by Anyone]</code>
• /delallg - <code>To delete all global filters from the bot's database.</code>
• /deletefiles - <code>To delete CamRip and PreDVD files from the bot's database.</code>"""

    FILE_STORE_TXT = """
<b>File Store is the feature which will create a shareable link of a single or multiple files.</b>

Available commands:
• /batch - <code>To create a batch link of multiple files.</code>
• /link - <code>To create a single file store link.</code>
• /pbatch - <code>Just like /batch, but the files will be sent with forward restrictions.</code>
• /plink - <code>Just like /link, but the file will be sent with forward restrictions.</code>"""

    STATUS_TXT = """<b>★ Total Files: <code>{}</code>
★ Total Users: <code>{}</code>
★ Total Chats: <code>{}</code>
★ Used Storage: <code>{}</code>
★ Free Storage: <code>{}</code></b>"""

    LOG_TEXT_G = """#NewGroup
Group = {}(<code>{}</code>)
Total Members = <code>{}</code>
Added By - {}"""

    LOG_TEXT_P = """#NewUser
ID - <code>{}</code>
Name - {}"""

    ALRT_TXT = """Hello {},
This is not your movie request,
Request yours..."""

    OLD_ALRT_TXT = """Hey {},
You are using one of my old messages,
Please send the request again."""

    CUDNT_FND = """I couldn't find anything related to {}
Did you mean any one of these?"""

    I_CUDNT = """Sorry, no files were found for your request {} 😕
Check your spelling in Google and try again 😃

Movie request format 👇
Example: Uncharted or Uncharted 2022 or Uncharted En

Series request format 👇
Example: Loki S01 or Loki S01E04 or Lucifer S03E24

🚯 Don't use ➠ ':(!,./)"""

    I_CUD_NT = """I couldn't find any movie related to {}.
Please check the spelling on Google or IMDb..."""

    MVE_NT_FND = """Movie not found in database..."""

    TOP_ALRT_MSG = """Checking for Movie in Database..."""

    MELCOW_ENG = """<b>Hello {} 😍, and welcome to {} Group...</b>"""

    OWNER_INFO = """
<b>⍟───[ Owner Details ]───⍟
    
• Full Name: Joel Kurian Biju
• Username: @creatorbeatz
• Permanent DM Link: <a href='t.me/creatorbeatz'>Click here</a></b>"""

    REQINFO = """
⚠ Information ⚠

This message will be automatically deleted after 10 minutes.

If you do not see the requested movie/series file, check the next page."""

    MINFO = """
⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯
Movie Request Format
⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯

Go to Google ➠ Type the movie name ➠ Copy the correct name ➠ Paste in this group

Example: Uncharted

🚯 Do not use ➠ ':(!,./)"""

    SINFO = """
⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯
Series Request Format
⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯

Go to Google ➠ Type the series name ➠ Copy the correct name ➠ Paste in this group

Example: Loki S01E01

🚯 Do not use ➠ ':(!,./)"""

    NORSLTS = """#NoResults
    
ID <b>: {}</b>
Nane <b>: {}</b>
Query <b>: {}</b>"""

    CAPTION = """
<b>📂 File Name : </b> <code>{file_name}</code></b>"""

    IMDB_TEMPLATE_TXT = """
<b>Query: {query}
IMDb Data:

🏷 Title: <a href={url}>{title}</a>
🎭 Genres: {genres}
📆 Year: <a href={url}/releaseinfo>{year}</a>"""

    RESTART_TXT = """#BotRestarted
    
<b>Bot Restarted!

📅 Date: <code>{}</code>
⏰ Time: <code>{}</code>
🌐 Timezone: <code>Asia/Kolkata</code>
🛠️ Build Status: <code>v1.0.0</code></b>"""

    LOGO = """
iPapkorn Bot"""
