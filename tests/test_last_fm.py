# Project Libraries
import last_fm_api as fm

# General Libraries
from unittest import TestCase



class TestLastFm(TestCase):

    def test_genre_counts(self):
        counts = fm.genre_counts()
        # for i in counts:
        #     print(i)

        self.assertEqual((518, 'male vocals'), counts[0], "genre counts")
        self.assertEqual((225, 'energetic'), counts[3], "genre counts")


    def test_albums_for_genres(self):
        genres = ['Gospel']
        albums_dict = fm.albums_for_genres(genres)
        # print(albums_dict)
        self.assertEqual(4, len(albums_dict), "simple album dict retrieval")
        self.assertTrue('Lady Soul' in albums_dict, "simple album dict retrieval")
        album = albums_dict['Lady Soul']
        self.assertTrue('Gospel' in album.moods, "simple album dict retrieval")
        # print(album)

        genres = ['warm', 'summer']
        albums_dict = fm.albums_for_genres(genres)

        self.assertEqual(191, len(albums_dict), "compound album dict retrieval")
        self.assertTrue('Gal Costa' in albums_dict, "compound album dict retrieval")
        album = albums_dict['Gal Costa']
        self.assertTrue('warm' in album.moods, "compound album dict retrieval")
        self.assertTrue('summer' in album.moods, "compound album dict retrieval")
        # print(album)

    def test_album_songs(self):
        genres = ['Gospel']
        albums_dict = fm.albums_for_genres(genres)
        albums_dict = fm.populate_songs(albums_dict)

        # print(albums_dict)
        self.assertEqual(4, len(albums_dict), "simple album dict retrieval")
        self.assertTrue('Lady Soul' in albums_dict, "simple album dict retrieval")
        album = albums_dict['Lady Soul']
        # print(album)
        # print(len(album.songs))
        # print(album.songs)
        self.assertEqual(14, len(album.songs), "simple album songs loading")
        self.assertTrue('Come Back Baby' in album.songs, "simple album songs loading")
