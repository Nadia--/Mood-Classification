# Project Libraries
import rate_my_music_api as rmm
from youtube_song import YouTubeSong
from data_obtainer.audio_downloader.download_audio import download_audio

# General Libraries
import json
import logging

DATA_DIRECTORY = "./../../data/rate_my_music/dictionaries/"

"""
API for downloading songs from YouTube based off Pavle's RateMyMusic data
"""

def save_video_id_to_moods(video_id_to_moods, moods, counter, depth):
    """ Helper function to save video_id_to_moods dictionary """

    descriptor = 'all_moods'
    if moods is not None:
        descriptor = '-'.join(moods)

    filename = DATA_DIRECTORY + descriptor + '-' + str(counter) + '-' + str(depth)

    with open(filename, 'w') as fp:
        json.dump(video_id_to_moods, fp)

def load_video_id_to_moods(moods, counter):
    """ Helper function to load video_id_to_moods dictionary """
    filename = '-'.join(moods) + '-' + str(counter)
    with open(DATA_DIRECTORY + filename, 'r') as f:
        dictionary = json.loads(f.read())
    return dictionary

def download_rate_my_music_data(moods, limit=None, depth=1):
    """
    Gathers all albums from Last.Fm data that have any of mood labels
    Downloads songs from YouTube corresponding to songs from those albums
    Saves a (YouTube video id, moods) dictionary for all successfully downloaded songs

    :param moods: Last.Fm moods we are interested in
    :param limit: maximum number of songs to work with
    :param depth: the max number of songs to extract from every album
    """

    albums = rmm.albums_for_moods(moods)
    albums = rmm.populate_songs(albums)

    print("Downloading songs from %d albums" % len(albums))

    video_id_to_moods = {}
    error_counter = 0
    counter = 0

    for rate_my_music_album in albums.values():
        if limit and counter == limit:
            break
        else:
            counter += 1

        artist = rate_my_music_album.artist
        songs = rate_my_music_album.songs
        song_moods = rate_my_music_album.moods

        for song_idx in range(depth):
            if song_idx >= len(songs):
                break
            song = songs[song_idx]

            print("\nalbum %d; artist: %s, title: %s, moods: %s" % (counter, artist, song, song_moods))

            song = YouTubeSong(artist=artist, title=song)
            song.fetch_video_id()
            if song.error:
                error_counter += 1
                logging.warning("Error finding a YouTube video id for this song, skipping!")
                continue

            # TODO: parse for the words full album in title in video_id query in addition to this

            # Songs longer than 25 minutes tend to be either giant orchestral pieces or full albums
            if not song.is_good_duration(1*60, 25*60):
                error_counter += 1
                logging.warning("Video id " + song.video_id + " duration error: " + song.error + ", skipping!")
                continue

            youtube_video_id = song.video_id
            print("youtube video_id = %s" % youtube_video_id)

            if download_audio(video_id=youtube_video_id):
                video_id_to_moods[youtube_video_id + '.mp3'] = list(song_moods)
                # TODO: create a reverse hashtable as well or at least moods counts
            else:
                error_counter += 1
                logging.warning("Exception occurred with download, skipping!")
                continue

    save_video_id_to_moods(video_id_to_moods, moods, counter, depth)

download_rate_my_music_data(None, depth=2)