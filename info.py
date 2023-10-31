import re
from os import environ
from Script import script

id_pattern = re.compile(r'^\d+$')

def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot Information
SESSION = environ.get('SESSION', 'Media_search')
API_ID = int(environ.get('API_ID'))
API_HASH = environ.get('API_HASH')
BOT_TOKEN = environ.get('BOT_TOKEN')

# Bot Settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = is_enabled(environ.get('USE_CAPTION_FILTER', 'True'), True)

# Pics and Videos
PICS = environ.get('PICS', 'https://telegra.ph/file/9b4816b9dd6af75e4e161.jpg https://telegra.ph/file/6e57f4e8fe85929cfd5ba.jpg https://telegra.ph/file/cea9b73befc6d6f92ebf9.jpg https://telegra.ph/file/1ab5619e0e22622ea6660.jpg https://telegra.ph/file/9ce8ca963f2b834f3b1d6.jpg').split()
NOR_IMG = environ.get("NOR_IMG", "https://telegra.ph/file/46443096bc6895c74a716.jpg")
MELCOW_PIC = environ.get("MELCOW_PIC", "https://telegra.ph/file/379d177bccabc5338759e.jpg")
MELCOW_VID = environ.get("MELCOW_VID", "https://telegra.ph/file/451f038b4e7c2ddd10dc0.mp4")
SPELL_IMG = environ.get("SPELL_IMG", "https://telegra.ph/file/a159414571d46bc15f8e7.jpg")

# Admins, Channels & Users
support_chat_id = environ.get('SUPPORT_CHAT_ID')
SUPPORT_CHAT_ID = int(support_chat_id) if support_chat_id and id_pattern.search(support_chat_id) else None
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '0').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = environ.get('AUTH_CHANNEL')
auth_grp = environ.get('AUTH_GROUP')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None
reqst_channel = environ.get('REQST_CHANNEL_ID')
REQST_CHANNEL = int(reqst_channel) if reqst_channel and id_pattern.search(reqst_channel) else None
NO_RESULTS_MSG = is_enabled(environ.get("NO_RESULTS_MSG", 'False'), False)

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "")
DATABASE_NAME = environ.get('DATABASE_NAME', "")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Telegram_files')

# Other Chats
MAIN_CHANNEL = environ.get('MAIN_CHANNEL', 'https://t.me/+1_i5rQjjG6pmNzY1')
BOTS_CHANNEL = environ.get('BOTS_CHANNEL', 'https://t.me/+UQSz8l_tSqc3MjJl')
UPDATE_CHANNEL = environ.get('UPDATE_CHANNEL', 'https://t.me/+sbXkYLOq0jtlMDc1')
DELETE_CHANNELS = [int(dch) if id_pattern.search(dch) else dch for dch in environ.get('DELETE_CHANNELS', '0').split()]
FILE_STORE_CHANNEL = [int(ch) for ch in environ.get('FILE_STORE_CHANNEL', '').split()]
FILE_FORWARD = environ.get('FILE_FORWARD', 'https://t.me/+cE93WntIF1IyOWVl')
FILE_CHANNEL = int(environ.get('FILE_CHANNEL', 0))
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', 0))
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'iPepkornSupport')
SUPPORT_GROUP = environ.get('SUPPORT_GROUP', 'https://t.me/+Eqy9OBo2MPBlOWJl')

# Verification and short link settings
IS_VERIFY = is_enabled(environ.get('IS_VERIFY', 'False'), False)
HOW_TO_VERIFY = environ.get('HOW_TO_VERIFY', "https://t.me/c/1845700490/3")
VERIFY2_URL = environ.get('VERIFY2_URL', "mdisklink.link")
VERIFY2_API = environ.get('VERIFY2_API', "4fa150d44b4bf6579c24b33bbbb786dbfb4fc673")
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'clicksfly.com')
SHORTLINK_API = environ.get('SHORTLINK_API', 'c2150e28189cefefd05f8a9c5c5770cc462033e3')

# Settings Configuration
SINGLE_BUTTON = is_enabled(environ.get('SINGLE_BUTTON', "True"), True)
PROTECT_CONTENT = is_enabled(environ.get('PROTECT_CONTENT', "True"), True)
IMDB = is_enabled(environ.get('IMDB', "True"), True)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
MELCOW_NEW_USERS = is_enabled(environ.get('MELCOW_NEW_USERS', "True"), True)
AUTO_FFILTER = is_enabled(environ.get('AUTO_FFILTER', "True"), True)
AUTO_DELETE = is_enabled(environ.get('AUTO_DELETE', "True"), True)
MAX_B_TN = environ.get("MAX_B_TN", "5")
IS_SHORTLINK = is_enabled(environ.get('IS_SHORTLINK', 'False'), False)

# Other Configuration
PORT = environ.get("PORT", "8080")
MSG_ALRT = environ.get('MSG_ALRT', 'What are you looking at ?')
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", script.CAPTION)
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
PUBLIC_FILE_STORE = is_enabled(environ.get('PUBLIC_FILE_STORE', "True"), True)
P_TTI_SHOW_OFF = is_enabled(environ.get('P_TTI_SHOW_OFF', "False"), False)
MAX_BTN = is_enabled(environ.get('MAX_BTN', "True"), True)
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", script.IMDB_TEMPLATE_TXT)

LOG_STR = "Current Customized Configurations are:-\n"
LOG_STR += ("IMDB Results are enabled, the bot will show IMDb details for your queries.\n" if IMDB else "IMBD Results are disabled.\n")
LOG_STR += ("P_TTI_SHOW_OFF found, users will be redirected to send /start to the Bot PM instead of sending a file directly.\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF is disabled, files will be sent in PM, instead of sending a start.\n")
LOG_STR += ("SINGLE_BUTTON is Found, filename and file size will be shown in a single button instead of two separate buttons.\n" if SINGLE_BUTTON else "SINGLE_BUTTON is disabled, filename and file size will be shown as different buttons.\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}, your files will be sent along with this customized caption.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION Found, default captions of the file will be used.\n")
LOG_STR += ("Long IMDb storyline enabled.\n" if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION is disabled, the plot will be shorter.\n")
LOG_STR += ("Spell Check Mode Is Enabled, the bot will suggest related movies if a movie is not found.\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY Mode disabled.\n")
LOG_STR += (f"MAX_LIST_ELM Found, a long list will be shortened to the first {MAX_LIST_ELM} elements.\n" if MAX_LIST_ELM else "The full list of casts and crew will be shown in the IMDb template, restrict them by adding a value to MAX_LIST_ELM.\n")
LOG_STR += f"Your current IMDb template is {IMDB_TEMPLATE}"
