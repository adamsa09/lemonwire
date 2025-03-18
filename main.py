"""
A python program to fetch music from youtube as .mp3 and apply tags in the metadata.
"""

from re import search
import eyed3
import urllib.parse
from bs4 import BeautifulSoup
from pytubefix import YouTube
import os
from moviepy import *
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

banner = """
   __  __/ /_   ____ ___  ____ |__  /   / /_____ _____ _____ ____  _____
  / / / / __/  / __ `__ \/ __ \ /_ <   / __/ __ `/ __ `/ __ `/ _ \/ ___/
 / /_/ / /_   / / / / / / /_/ /__/ /  / /_/ /_/ / /_/ / /_/ /  __/ /    
 \__, /\__/  /_/ /_/ /_/ .___/____/   \__/\__,_/\__, /\__, /\___/_/     
/____/                /_/                      /____//____/
------------------------------------------------------------------------


"""

print(banner)

# --------------------------------------

def get_song_links(search_url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # Run with no GUI
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Load the page
    driver.get(search_url)

    # Get the source code of the webpage
    html = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Close the browser process
    driver.quit()

    links = []

    # Get all links to youtube videos
    for a in html.find_all('a', href=True):
        href = a.get('href')
        if '/watch?' in href:
            links.append(f'https://youtube.com{href}')

    return links

def compile_search_url(name, artist):
    complete_song = f'{name} by {artist}'

    full_url = f'{yt_base_search}{complete_song}'

    search_url = urllib.parse.quote(full_url, safe='/:?=&', encoding=None, errors=None)
    return search_url

def create_mp3(song_name):
    for file in os.listdir():
        if file.endswith('.mp4'):
            videofile = file
            video = VideoFileClip(videofile)
            if song_name != '':
                video.audio.write_audiofile(f'{song}.mp3', codec='libmp3lame')
            else:
                # If no song name is supplied, use the video name
                video.audio.write_audiofile(f'{file.removesuffix('.mp4')}.mp3', codec='libmp3lame')
            video.close()
            os.remove(videofile)

def cleanup():
    pass
    # to_remove = []
    # for file in os.listdir():
    #     if file.endswith('.mp4'):
    #         to_remove.append(file)

    # # Close any open video handles
    # import gc
    # gc.collect()

    # for file in to_remove:
    #     try:
    #         os.remove(file)
    #     except PermissionError:
    #         print(f"[!] Could not remove {file}. File may be in use.")
    
def apply_tags(song, artist):
    audiofile = eyed3.load(f'{song}.mp3')
    audiofile.tag.title = song
    audiofile.tag.artist = artist
    audiofile.tag.save()

def send_to_spotify_folder():
    config = json.loads(open('config.json', 'r').read())
    if config['spotify-save-location'] == '':
        print('Please set the Spotify folder path in the config file')
        return
    
    for file in os.listdir():
        if file.endswith('.mp3'):
            # Send the file to the spotify save directory
            os.rename(file, f'{config["spotify-save-location"]}/{file}')

def getSong(song, artist):
    print('[i] Retrieving Song link')

    search_url = compile_search_url(song, artist)

    song_link = get_song_links(search_url)[0]

    print(f'[i] Found Song: {song_link}')

    YouTube(song_link).streams.first().download()

    print('[i] Extracting .mp3 from song')

    create_mp3(song)

    print('[i] Applying Metadata')

    apply_tags(song, artist)

    print('[i] Moving to Spotify')

    send_to_spotify_folder()

    print('[i] Cleaning up')
    cleanup()

def getPlaylist(playlist_link):
    print('[i] Retrieving Playlist links')
    
    all_links = get_song_links(playlist_link)
    song_links = []
    for k in range(len(all_links)):
        if 'index' in all_links[k] and all_links[k] not in song_links:
            song_links.append(all_links[k])
    
    for i in range(len(song_links)):
        YouTube(song_links[i]).streams.first().download()
        create_mp3('')
        # TODO: Apply tags for each mp3 created.
        send_to_spotify_folder()
        cleanup()


# -------------------------------------------------------------------

yt_base_search = 'https://www.youtube.com/results?search_query='

mode = input('Select mode: ')

if int(mode) == 1:
    song = input('Song Name: ')
    artist = input('Song Artist: ')
    getSong(song, artist)
elif int(mode) == 2:
    playlist_link = input('Playlist Link: ')
    getPlaylist(playlist_link)