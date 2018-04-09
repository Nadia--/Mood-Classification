# Project Libraries
import filter as fltr
from song_aggregate import SongAggregateScraper

# General Libraries
from unittest import TestCase

BASEDIR = '../../../../Thesis/data_sample/W/D/I'

class TestSavingLoading(TestCase):
    def test_save_and_load(self):
        MIN_NUM_COMMENTS = 10
        MAX_NUM_COMMENTS = 80
        limit = 5
        filter_list = [fltr.english_filter]

        aggr = SongAggregateScraper()
        aggr.scrape(BASEDIR, MIN_NUM_COMMENTS, MAX_NUM_COMMENTS, filter_list, limit=limit)
        good_songs = aggr.get_passing_songs()
        self.assertTrue(aggr.max_num_comments == MAX_NUM_COMMENTS, "aggregator metadata")
        self.assertTrue(aggr.aggregate[3] == 2, "aggregate statistics")
        self.assertTrue(len(good_songs) == 1, "scraper passing songs")
        self.assertEqual(good_songs[0].comments[0], "Who still listening in 2018?", "passing songs comments")

        aggr.save_to_file('test_file')

        aggr2 = SongAggregateScraper()
        self.assertTrue(aggr2.max_num_comments is None, "aggr2 is empty")

        aggr2.load_from_file('test_file')
        recover_good_songs = aggr2.get_passing_songs()
        self.assertEqual(aggr.max_num_comments, aggr2.max_num_comments, "metadata preserved")
        self.assertEqual(aggr.aggregate[3], aggr2.aggregate[3], "aggregate statistics preserved")
        self.assertEqual(len(good_songs[0].comments), len(recover_good_songs[0].comments), "passing songs preserved")
        self.assertEqual(good_songs[0].comments[0], recover_good_songs[0].comments[0], "passing songs comments preserved")

