# Project Libraries
import last_fm_api as fm
from youtube_song import YouTubeSong
from download_audio import download_audio

# General Libraries
import json


def save_video_id_dictionary(video_id_dictionary, moods, counter):
    filename = fm.BASE_DIRECTORY + '-'.join(moods) + '-' + str(counter)
    with open(filename, 'w') as fp:
        json.dump(video_id_dictionary, fp)

def load_video_id_dictionary(moods, counter):
    filename = '-'.join(moods) + '-' + str(counter)
    return fm.load_dictionary(filename)


def download_last_fm_data(moods, limit=None):
    albums = fm.albums_for_genres(moods)
    albums = fm.populate_songs(albums)

    print(len(albums))

    video_id_dictionary = {}
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

        print("\nartist: %s, title: %s, moods: %s" % (artist, song, song_moods))

        song = YouTubeSong(artist=artist, title=song)
        song.fetch_video_id()
        if song.error:
            error_counter += 1
            break

        youtube_video_id = song.video_id
        print("youtube video_id = %s" % youtube_video_id)

        download_audio(video_ids=[youtube_video_id])

        video_id_dictionary[youtube_video_id] = list(song_moods)

    save_video_id_dictionary(video_id_dictionary, moods, counter)


