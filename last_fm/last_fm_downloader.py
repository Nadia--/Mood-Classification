# Project Libraries
import last_fm_api as fm
from youtube_song import YouTubeSong
from download_audio import download_audio

# General Libraries
import json
import logging

"""
API for downloading songs from YouTube based off Pavle's Last.Fm data
"""

def save_video_id_to_moods(video_id_to_moods, moods, counter):
    """ Helper function to save video_id_to_moods dictionary """
    filename = fm.BASE_DIRECTORY + '-'.join(moods) + '-' + str(counter)
    with open(filename, 'w') as fp:
        json.dump(video_id_to_moods, fp)

def load_video_id_to_moods(moods, counter):
    """ Helper function to load video_id_to_moods dictionary """
    filename = '-'.join(moods) + '-' + str(counter)
    return fm.load_dictionary(filename)

def download_last_fm_data(moods, limit=None):
    """
    Gathers all albums from Last.Fm data that have any of mood labels
    Downloads songs from YouTube corresponding to songs from those albums
    Saves a (YouTube video id, moods) dictionary for all successfully downloaded songs

    :param moods: Last.Fm moods we are interested in
    :param limit: maximum number of songs to work with
    """

    albums = fm.albums_for_moods(moods)
    albums = fm.populate_songs(albums)

    print("Downloading songs from %d albums" % len(albums))

    video_id_to_moods = {}
    error_counter = 0
    counter = 0

    for last_fm_album in albums.values():
        if limit and counter == limit:
            break
        else:
            counter += 1

        # TODO: using just the first song for a more even spread (for now)
        artist = last_fm_album.artist
        song = last_fm_album.songs[0]
        song_moods = last_fm_album.moods

        print("\nalbum %d; artist: %s, title: %s, moods: %s" % (counter, artist, song, song_moods))

        song = YouTubeSong(artist=artist, title=song)
        song.fetch_video_id()
        if song.error:
            error_counter += 1
            logging.warning("Error finding a YouTube video id for this song, skipping!")
            continue

        youtube_video_id = song.video_id
        print("youtube video_id = %s" % youtube_video_id)

        # TODO: do not include pieces of over 15 minutes as part of the data set (full albums)
        if download_audio(video_id=[youtube_video_id]):
            video_id_to_moods[youtube_video_id] = list(song_moods)
        else:
            logging.warning("Exception occurred with download, skipping!")
            continue

    save_video_id_to_moods(video_id_to_moods, moods, counter)


