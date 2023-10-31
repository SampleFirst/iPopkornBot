import pyrogram
from pyrogram import Client, filters
import requests
from bs4 import BeautifulSoup

# Define the command to trigger the bot
@Client.on_message(filters.command(["insta"]))
async def download_instagram_media(client, message):
    try:
        # Extract the Instagram post or reel link from the user's message
        command_parts = message.text.split(" ")
        if len(command_parts) != 2:
            await message.reply("Invalid command format. Use /ddinstagram <Instagram Link>")
            return

        instagram_link = command_parts[1]

        # Check if the link is from Instagram
        if "instagram.com" not in instagram_link:
            await message.reply("This is not an Instagram link.")
            return

        # Fetch the page content of the Instagram link
        response = requests.get(instagram_link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Check if it's an image or video
            if "/p/" in instagram_link:
                # This is a post link
                image_tags = soup.find_all("meta", property="og:image")
                image_urls = [tag["content"] for tag in image_tags]
                for image_url in image_urls:
                    await message.reply_photo(image_url)
            elif "/reel/" in instagram_link:
                # This is a reel link
                video_url = soup.find("meta", property="og:video")["content"]
                await message.reply_video(video_url)
            else:
                await message.reply("No media found on this Instagram link.")
        else:
            await message.reply("Unable to fetch content from the Instagram link.")
    except Exception as e:
        print(e)
        await message.reply("An error occurred while processing the request.")
        
