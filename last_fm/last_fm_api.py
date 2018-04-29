# Project Libraries

# General Libraries
import json

BASE_DIRECTORY = "./../data/last_fm_data/"
MOODS_FILE = 'genre_to_artist-title'
ALBUMS_FILE = 'album_to_songs'


class LastFmAlbum:
    def __init__(self, album_name, artist):
        self.album_name = album_name
        self.artist = artist
        self.moods = set()
        self.songs = None

    def add_genre(self, genre):
        self.moods = self.moods.union({genre})

    def __repr__(self):
        return "album: %s, artist: %s, moods: %s, songs: %s" % (self.album_name, self.artist, self.moods, self.songs)


def load_dictionary(filename):
    with open(BASE_DIRECTORY + filename, 'r') as f:
        dictionary = json.loads(f.read())
    return dictionary


def genre_counts():
    genre_dict = load_dictionary(MOODS_FILE)
    genre_counts = []
    for genre, albums in genre_dict.items():
        genre_counts.append((len(albums), genre))

    genre_counts.sort(reverse=True)
    return genre_counts


def parse_entry(entry):
    qualifiers = entry.split("-")
    if len(qualifiers) == 2:
        return qualifiers[0], qualifiers[1]
    else:
        return None


def add_album_to_dictionary(album_dictionary, artist_album, genre):
    artist = artist_album[0]
    album = artist_album[1]

    if album not in album_dictionary:
        last_fm_album = LastFmAlbum(album, artist)
        album_dictionary[album] = last_fm_album

    album_dictionary[album].add_genre(genre)


def albums_for_genres(genres):
    album_dictionary = {}

    genre_dict = load_dictionary(MOODS_FILE)
    bad_parse_ctr = 0

    for genre in genres:
        entries = genre_dict[genre]
        for entry in entries:
            parsed_entry = parse_entry(entry)
            if parsed_entry is None:
                bad_parse_ctr += 1
            else:
                add_album_to_dictionary(album_dictionary, parsed_entry, genre)

    return album_dictionary


def populate_songs(album_dictionary):
    album_to_songs_dict = load_dictionary(ALBUMS_FILE)

    for album, last_fm_album in album_dictionary.items():
        last_fm_album.songs = album_to_songs_dict[album]

    return album_dictionary
