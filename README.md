# Lemonwire: Youtube song downloader and auto-tagger
A python based tool that gets music from YouTube as `.mp3` and adds the correct metadata tags to it.

## Dependencies
- [Selenium](https://selenium-python.readthedocs.io/) & [Beautifulsoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) for fetching videos
- [Pytube](https://pytube.io/) for downloading videos
- [Pymovie](https://zulko.github.io/moviepy/) for transforming `.mp4` into `.mp3` files
- [eyeD3](https://eyed3.readthedocs.io/) for tagging `.mp3` files

## Ideas
- **Metadata tagging**
	- Use AI APIs to automatically tag
	- Ability to download entire youtube playlists
    	- Would need AI integration to deduce song artists & title from each video