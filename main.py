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
  _                          _         
 | |___ _ __  ___ _ ___ __ _(_)_ _ ___ 
 | / -_) '  \\/ _ \\ ' \\ V  V / | '_/ -_)
 |_\\___|_|_|_\\___/_||_\\_/\\_/|_|_| \\___|
------------------------------------------------------------------------


"""

# --------------------------------------

def get_song_links(search_url):
    print('[i] Fetching song links...')
    # Set up the browser
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

def compile_search_url(song_name, artist, yt_base_search):
    print('[i] Compiling search URL...')
    # Compile the search URL
    complete_song = f'{song_name} by {artist}'

    full_url = f'{yt_base_search}{complete_song}'

    search_url = urllib.parse.quote(full_url, safe='/:?=&', encoding=None, errors=None)
    return search_url

def transform_to_mp3(song_name):
    print('[i] Converting to mp3...')
    for file in os.listdir():
        # If the file is a .mp4, convert it to .mp3
        if file.endswith('.mp4'):
            videofile = file
            video = VideoFileClip(videofile)
            if song_name != '':
                video.audio.write_audiofile(f'{song_name}.mp3', codec='libmp3lame') # Create mp3 with specified song name
            else:
                # If no song name is supplied, use the video name
                video.audio.write_audiofile(f'{file.removesuffix('.mp4')}.mp3', codec='libmp3lame')
            video.close()
            os.remove(videofile)
    
def apply_tags(filename, artist):
    print('[i] Applying tags...')
    audiofile = eyed3.load(f'{filename}.mp3')
    audiofile.tag.title = filename
    audiofile.tag.artist = artist
    audiofile.tag.save()

def send_to_spotify_folder():
    print('[i] Sending to Spotify folder...')
    # Get the spotify local files folder from the config.json file
    config = json.loads(open('config.json', 'r').read())
    if config['spotify-save-location'] == '':
        print('Please set the Spotify folder path in the config file')
        return
    
    # Send the mp3 to the spotify folder
    for file in os.listdir():
        if file.endswith('.mp3'):
            # Send the file to the spotify save directory
            os.rename(file, f'{config["spotify-save-location"]}/{file}')

def getSong(song, artist, yt_base_search):
    print('[i] Fetching song...')
    search_url = compile_search_url(song, artist, yt_base_search)

    song_link = get_song_links(search_url)[0]

    YouTube(song_link).streams.first().download()

    transform_to_mp3(song)

    apply_tags(song, artist)

    send_to_spotify_folder()

def get_song_name():
    # TODO: Implement AI to get song name and artist
    pass

def getPlaylist(playlist_link):
    print('[i] Fetching playlist...')    
    all_links = get_song_links(playlist_link)
    song_links = []
    for k in range(len(all_links)):
        if 'index' in all_links[k] and all_links[k] not in song_links:
            song_links.append(all_links[k])
    
    for i in range(len(song_links)):
        YouTube(song_links[i]).streams.first().download()
        song_name, artist = get_song_name() # TODO
        transform_to_mp3('')
        apply_tags(song_name, artist)
        send_to_spotify_folder()

def main():
    yt_base_search = 'https://www.youtube.com/results?search_query='

    while True:
        os.system('cls')
        print(banner)
        print('1. Single Song')
        print('2. Playlist')
        print('q. Quit')
        mode = input('Select mode: ')

        if mode == 'q':
            print('Exiting...')
            exit()
        elif int(mode) == 1:
            song = input('Song Name: ')
            artist = input('Song Artist: ')
            getSong(song, artist, yt_base_search)
        elif int(mode) == 2:
            playlist_link = input('Playlist Link: ')
            getPlaylist(playlist_link)
        else:
            print('Invalid mode selected. Exiting.')
            exit()

if __name__ == '__main__':
    main()
