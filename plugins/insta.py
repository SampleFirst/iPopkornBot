import os
import shutil
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from youtube-dl

# Create a directory to save downloaded media files in HD
os.makedirs("instagram_media", exist_ok=True)

# Define the command to trigger the bot
@Client.on_message(filters.command(["insta"]))
async def download_instagram_media(client, message):
    try:
        # Extract the Instagram post or reel link from the user's message
        command_parts = message.text.split(" ")
        if len(command_parts) != 2:
            await message.reply("Invalid command format. Use /insta <Instagram Link>")
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

            # Check if it's a video (reel) or an image
            video_url = soup.find("meta", property="og:video")
            image_url = soup.find("meta", property="og:image")

            if video_url:
                # Download and send the video in HD
                video_url = video_url["content"]
                video_filename = os.path.join("instagram_media", "video.mp4")

                # Download the video in HD quality
                os.system(f'youtube-dl -f "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/mp4" -o "{video_filename}" "{video_url}"')

                if os.path.exists(video_filename):
                    await message.reply_video(video_filename)
                else:
                    await message.reply("Unable to fetch the video from the Instagram link.")
            elif image_url:
                # Download and send all images in HD
                image_url = image_url["content"]
                image_filenames = []

                # Download all images in HD quality
                image_data = requests.get(image_url, stream=True)
                if image_data.status_code == 200:
                    image_filename = os.path.join("instagram_media", "image.jpg")
                    with open(image_filename, 'wb') as file:
                        for chunk in image_data.iter_content(1024):
                            file.write(chunk)
                    image_filenames.append(image_filename)

                for idx, image_file in enumerate(image_filenames):
                    await message.reply_photo(photo=image_file, caption=f"Image {idx + 1}")

                # Clean up the downloaded image files
                shutil.rmtree("instagram_media")
            else:
                await message.reply("No media found on this Instagram link.")
        else:
            await message.reply("Unable to fetch content from the Instagram link.")
    except Exception as e:
        print(e)
        await message.reply("An error occurred while processing the request.")
