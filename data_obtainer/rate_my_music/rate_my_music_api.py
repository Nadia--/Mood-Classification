# Project Libraries

# General Libraries
import json

BASE_DIRECTORY = "./../data/rate_my_music_data/"
MOODS_FILE = 'genre_to_artist-title'
ALBUMS_FILE = 'album_to_songs'

""" 
API for working with Pavle's RateMyMusic data set
"""

# TODO: not LastFm but RateMyMusic.com

class RateMyMusicAlbum:
    """
    RateMyMusicAlbum object stores artist, moods, and songs, which are necessary for
    1) downloading audio tracks from YouTube by artist, song
    2) classifying said songs by moods
    """
    def __init__(self, album_name, artist):
        self.album_name = album_name
        self.artist = artist
        self.moods = set()
        self.songs = []

    def add_mood(self, mood):
        self.moods = self.moods.union({mood})

    def __repr__(self):
        return "album: %s, artist: %s, moods: %s, songs: %s" % (self.album_name, self.artist, self.moods, self.songs)


def load_dictionary(filename):
    """ Helper function to load a dictionary from rate_my_music_data by filename """
    with open(BASE_DIRECTORY + filename, 'r') as f:
        dictionary = json.loads(f.read())
    return dictionary


def mood_counts():
    """ Returns an array of tuples (mood, number of occurrences) sorted in order of highest count first """
    mood_dict = load_dictionary(MOODS_FILE)
    mood_counts = []
    for mood, albums in mood_dict.items():
        mood_counts.append((len(albums), mood))

    mood_counts.sort(reverse=True)
    return mood_counts


def parse_entry(entry):
    """ Rudimentary method for splitting artist-album string into artist and album strings """
    qualifiers = entry.split("-")
    if len(qualifiers) == 2:
        return qualifiers[0], qualifiers[1]
    else:
        return None


def add_album_to_dictionary(album_dictionary, artist_album, mood):
    """ Adds album to dictionary if it is not already in it, and adds mood to album's list of moods """
    artist = artist_album[0]
    album = artist_album[1]

    if album not in album_dictionary:
        last_fm_album = RateMyMusicAlbum(album, artist)
        album_dictionary[album] = last_fm_album

    album_dictionary[album].add_mood(mood)


def albums_for_moods(moods):
    """ Returns a dictionary of albums (with any mood from moods) mapped from album_title to RateMyMusicAlbum """
    album_dictionary = {}

    mood_dict = load_dictionary(MOODS_FILE)
    bad_parse_ctr = 0

    if moods is None:
        moods = mood_dict.keys()

    for mood in moods:
        entries = mood_dict[mood]
        for entry in entries:
            parsed_entry = parse_entry(entry)
            if parsed_entry is None:
                bad_parse_ctr += 1
            else:
                add_album_to_dictionary(album_dictionary, parsed_entry, mood)

    return album_dictionary


def populate_songs(album_dictionary):
    """ Updates all RateMyMusicAlbums in album_dictionary with songs from album_to_song file """
    album_to_songs_dict = load_dictionary(ALBUMS_FILE)

    for album, last_fm_album in album_dictionary.items():
        if album in album_to_songs_dict:
            last_fm_album.songs = album_to_songs_dict[album]

    return album_dictionary

