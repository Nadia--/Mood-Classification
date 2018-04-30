# Project Libraries

# General Libraries
from __future__ import unicode_literals
import youtube_dl  # https://github.com/rg3/youtube-dl/blob/master/README.md#embedding-youtube-dl

"""
API for downloading YouTube audio 
"""

YOUTUBE_VIDEO_URL = 'https://www.youtube.com/watch?v='

""" download options """
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'D:/Dropbox/AAA/Senior/242/final project/Final Project/data/youtube_data/songs/%(id)s.%(title)s.%(ext)s)',
    'download_archive': 'D:/Dropbox/AAA/Senior/242/final project/Final Project/data/youtube_data/songs/dl_archive',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}


def download_audio(video_id):
    """ Downloads audio files from a list of YouTube video ids """
    print(video_id)
    url = YOUTUBE_VIDEO_URL + video_id
    print(url)

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            return True
        except:
            return False


