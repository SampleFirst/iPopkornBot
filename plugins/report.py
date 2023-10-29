import pytz
from datetime import datetime, date
from Script import script
from info import LOG_CHANNEL
from database.users_chats_db import db
from utils import temp
import asyncio

async def send_report_message(self):
    while True:
        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        now = datetime.now(tz)
        formatted_date_1 = now.strftime("%d-%B-%Y")
        formatted_date_2 = today.strftime("%d %b")
        time = now.strftime("%H:%M:%S %p")

        total_users = await db.total_users_count()
        total_chats = await db.total_chat_count()
        today_users = await db.daily_users_count(today) + 1
        today_chats = await db.daily_chats_count(today) + 1

        if now.hour == 23 and now.minute == 59:
            await self.send_message(
                chat_id=LOG_CHANNEL,
                text=script.REPORT_TXT.format(
                    a=formatted_date_1,
                    b=formatted_date_2,
                    c=time,
                    d=total_users,
                    e=total_chats,
                    f=today_users,
                    g=today_chats,
                    h=temp.U_NAME
                )
            )
            # Sleep for 1 minute to avoid sending multiple messages
            await asyncio.sleep(60)
        else:
            # Sleep for 1 minute and check again
            await asyncio.sleep(60)
