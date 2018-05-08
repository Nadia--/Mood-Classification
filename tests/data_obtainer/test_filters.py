# Project Libraries
from song_aggregate import SongAggregateScraper
import filter as fltr

# General Libraries
from unittest import TestCase

SAVEFILE = 'test_filter_file'
english_filter = fltr.Filter('english-1000-word-filter', fltr.Action.REMOVE_EXCEPT, fltr.list_from_file('english_1000', 4))
length_filter = fltr.Filter('length-filter', fltr.Action.FILTER_BY_LENGTH, cutoff_lb=7, cutoff_ub=250)
brutish_music_filter = fltr.Filter('brutish_filter', fltr.Action.SUBSTRING_MATCH, fltr.list_from_file('music_words') | fltr.list_from_file('mood_words'))

class TestFilters(TestCase):

    def english_filter_3rd_song(self, filtered_comments):
        """ results of english filter applied to 3rd song """
        self.assertEqual(6, len(filtered_comments), "english filtered length")
        self.assertTrue('positive' in filtered_comments[0].lower(), "english in comment")
        self.assertTrue('single' in filtered_comments[1].lower(), "english in comment")
        self.assertTrue('best' in filtered_comments[2].lower(), "english in comment")
        self.assertTrue('continue' in filtered_comments[3].lower(), "english in comment")
        self.assertTrue('turn' in filtered_comments[4].lower(), "english in comment")
        self.assertTrue('come' in filtered_comments[5].lower(), "english in comment")

    def test_are_key_words_in_comment(self):
        """ Running english filter on a song with Brazilian comments """
        aggr = SongAggregateScraper()
        aggr.load_from_file(SAVEFILE)
        passing_songs = aggr.get_passing_songs()

        song = passing_songs[2]
        filtered_comments = []
        for idx, comment in enumerate(song.comments):
            #print(idx, comment)

            if english_filter.are_key_words_in_comment(comment):
                filtered_comments.append(comment)

        # for idx, comment in enumerate(filtered_comments):
        #     print(idx, comment)

        self.assertEqual(len(song.comments), 40, "unfiltered length")
        self.english_filter_3rd_song(filtered_comments)

    def test_run_filters_simple(self):
        """ testing run_filters method with english filter alone """
        aggr = SongAggregateScraper()
        aggr.load_from_file(SAVEFILE)
        passing_songs = aggr.get_passing_songs()

        song = passing_songs[2]
        filtered_comments = fltr.run_filters([english_filter], song.comments)
        self.english_filter_3rd_song(filtered_comments)

    def test_length_filter(self):
        """ Running a length filter on a song with lyrics as part of comments"""
        aggr = SongAggregateScraper()
        aggr.load_from_file(SAVEFILE)
        passing_songs = aggr.get_passing_songs()

        song = passing_songs[8]
        filtered_comments = fltr.run_filters([english_filter], song.comments)
        # for idx, comment in enumerate(filtered_comments):
        #     print(idx, comment)

        length_filtered_comments = fltr.run_filters([length_filter], filtered_comments)
        # for idx, comment in enumerate(length_filtered_comments):
        #     print(idx, comment)

        self.assertEqual(26, len(filtered_comments), "length unfiltered quantity")
        self.assertEqual(20, len(length_filtered_comments), "length filtered quantity")

    def test_run_filters_medium(self):
        """ testing english filter with the length filter """
        aggr = SongAggregateScraper()
        aggr.load_from_file(SAVEFILE)
        passing_songs = aggr.get_passing_songs()

        song = passing_songs[8]
        filtered_comments = fltr.run_filters([english_filter, length_filter], song.comments)
        # for idx, comment in enumerate(filtered_comments):
        #     print(idx, comment)

        self.assertEqual(20, len(filtered_comments), "run_filters 2 filters")

    def test_substring_match_filter(self):
        """ testing substring matching filter, for the word 'sing' """

        comment1 = 'hello I am singing'
        comment2 = 'hello I like to sing'
        comment3 = 'hello I do nothing'

        filtered_comments = fltr.run_filters([brutish_music_filter], [comment1, comment2, comment3])

        self.assertTrue(comment1 in filtered_comments, "substring match filter")
        self.assertTrue(comment2 in filtered_comments, "substring match filter")
        self.assertTrue(comment3 not in filtered_comments, "substring match filter")
