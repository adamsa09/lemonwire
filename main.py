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

def create_mp3(song):
    for file in os.listdir():
        if file.endswith('.mp4'):
            videofile = file

    video = VideoFileClip(videofile)
    video.audio.write_audiofile(f'{song}.mp3', codec='libmp3lame')

def cleanup():
    for file in os.listdir():
        if file.endswith('.mp4'):
            os.remove(file)

def apply_tags(song, artist):
    audiofile = eyed3.load(f'{song}.mp3')
    audiofile.tag.title = song
    audiofile.tag.artist = artist
    audiofile.tag.save()

def send_to_spotify_folder(song):
    config = json.loads(open('config.json', 'r').read())
    if config['spotify-save-location'] == '':
        print('Please set the Spotify folder path in the config file')
        return
    
    os.rename(f'{song}.mp3', f'{config["spotify-save-location"]}/{song}.mp3')

# -------------------------------------------------------------------

yt_base_search = 'https://www.youtube.com/results?search_query='

mode = input('Select mode: ')

if int(mode) == 1:
    song = input('Song Name: ')
    artist = input('Song Artist: ')

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

send_to_spotify_folder(song)

print('[i] Cleaning up')
cleanup()