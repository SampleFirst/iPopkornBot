import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

movie_links = {}
ddl_links = {}


@Client.on_message(filters.command("skymovies"))
async def skymovies(client, message):
    query = message.text.split(maxsplit=1)
    if len(query) == 1:
        await message.reply_text("Please provide a movie name to search.")
        return
    query = query[1]
    search_results = await message.reply_text("Processing...")
    movies_list = search_movies(query)
    if movies_list:
        keyboards = []
        for movie in movies_list:
            keyboard = [InlineKeyboardButton(movie["title"], callback_data=movie["id"])]
            keyboards.append(keyboard)
        reply_markup = InlineKeyboardMarkup(keyboards)
        await search_results.edit_text('Search Results...', reply_markup=reply_markup)
    else:
        await search_results.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')


@Client.on_callback_query(filters.regex('^len'))
async def movie_result(client, callback_query):
    query = callback_query
    movie_id = query.data
    msg = await query.message.reply_text("Processing...")
    download_list = get_movie(movie_links[movie_id])
    if download_list:
        keyboards = []
        for download in download_list:
            keyboard = [InlineKeyboardButton(download["text"], callback_data=download["link"])]
            keyboards.append(keyboard)
        reply_markup = InlineKeyboardMarkup(keyboards)
        await msg.delete()
        await query.message.reply_text("Choose Download Link:", reply_markup=reply_markup)
    else:
        await query.answer("No download links available for this movie.")


@Client.on_callback_query(filters.regex('^ddl'))
async def open_link_and_extract(client, callback_query):
    query = callback_query
    download_id = query.data
    msg = await query.message.reply_text("Processing...")
    finale_list = final_link_page(ddl_links[download_id])
    logger.info(f"Searching for: {finale_list}")
    keyboards = []
    for link in finale_list:
        domain = link.split("//")[-1].split("/")[0]
        keyboard = [InlineKeyboardButton(domain, url=link)]
        keyboards.append([keyboard])
    reply_markup = InlineKeyboardMarkup(keyboards)
    await msg.delete()
    await query.message.reply_text("Extracted Links:", reply_markup=reply_markup)
    

def search_movies(query):
    logger.info(f"Searching for movies with query: {query}")
    movies_list = []
    website = requests.get(f"https://skymovieshd.ngo/search.php?search={query.replace(' ', '+')}&cat=All")
    if website.status_code == 200:
        website = website.text
        website = BeautifulSoup(website, "html.parser")
        movies = website.find_all("div", {'class': 'L'})
        for movie in movies:
            movie_details = {}
            movie_link = movie.find("a", href=True)
            if movie_link:
                movie_details["id"] = f"len{movies.index(movie)}"
                movie_details["title"] = movie_link.text.strip()
                movie_links[movie_details["id"]] = movie_link['href']
                movies_list.append(movie_details)
    return movies_list


def get_movie(movie_page_url):
    download_list = []
    movie_page = "https://skymovieshd.ngo" + movie_page_url
    movie_page_link = requests.get(movie_page)
    logger.info(f"Searching first download link groups: {movie_page}")
    if movie_page_link.status_code == 200:
        movie_page_link = movie_page_link.text
        movie_page_link = BeautifulSoup(movie_page_link, "html.parser")
        download_links = movie_page_link.find("div", {'class': 'Bolly'})
        if download_links:
            download_links = download_links.find_all("a", href=True)
            for download in download_links:
                load_details = {}
                load_details["link"] = f"ddl{download_links.index(download)}"
                load_details["text"] = download.text.strip()
                ddl_links[load_details["link"]] = download['href']
                download_list.append(load_details)
    return download_list


def final_link_page(download_page_url):
    finale_list = []
    download_page = download_page_url
    webpage = requests.get(download_page)
    logger.info(f"Searching final download link: {download_page}")
    if webpage.status_code == 200:
        webpage = webpage.text
        webpage = BeautifulSoup(webpage, "html.parser")
        links = webpage.find_all("a", href=True, rel="external", target="_blank")
        for link in links:
            href = link['href']
            if href.startswith("https://"):
                finale_list.append(href)
    return finale_list
    
    
