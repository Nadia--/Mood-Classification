# Project Libraries
import filter as fltr
from song_aggregate import SongAggregateScraper
from five_million import random_songs

# General Libraries
from unittest import TestCase

BASEDIR = '../../../../Thesis/data_sample/W/D/I'
MIN_NUM_COMMENTS = 10
MAX_NUM_COMMENTS = 40
LIMIT = 5
FILTER_LIST = [fltr.english_filter]

# TODO: update this test; it is failing because the YouTube videos have been perturbed

class TestSavingLoading(TestCase):

    def test_scrape_echonest(self):
        aggr = SongAggregateScraper()
        aggr.scrape_from_echonest(BASEDIR, MIN_NUM_COMMENTS, MAX_NUM_COMMENTS, FILTER_LIST, limit=LIMIT)
        #aggr.print_summary()
        self.assertTrue(len(aggr.get_passing_songs()) >=2, "echonest youtube scraper")

    def test_scrape_5m(self):
        video_ids = random_songs(LIMIT, 0)

        aggr = SongAggregateScraper()
        aggr.scrape_video_ids(video_ids, MIN_NUM_COMMENTS, MAX_NUM_COMMENTS, FILTER_LIST)
        #aggr.print_summary()
        self.assertTrue(len(aggr.get_passing_songs()) >=2, "5 million youtube scraper")

    def test_save_and_load(self):
        aggr = SongAggregateScraper()
        aggr.scrape_from_echonest(BASEDIR, MIN_NUM_COMMENTS, MAX_NUM_COMMENTS, FILTER_LIST, limit=LIMIT)
        good_songs = aggr.get_passing_songs()
        aggr.save_to_file('test_file')
        # self.assertTrue(aggr.max_num_comments == MAX_NUM_COMMENTS, "aggregator metadata")
        # self.assertTrue(aggr.aggregate[3] == 2, "aggregate statistics")
        # self.assertTrue(len(good_songs) == 1, "scraper passing songs")
        # self.assertEqual(good_songs[0].comments[0], "Who still listening in 2018?", "passing songs comments")


        aggr2 = SongAggregateScraper()
        self.assertTrue(aggr2.max_num_comments is None, "aggr2 is empty")

        aggr2.load_from_file('test_file')
        recover_good_songs = aggr2.get_passing_songs()
        self.assertEqual(aggr.max_num_comments, aggr2.max_num_comments, "metadata preserved")
        self.assertEqual(aggr.aggregate[3], aggr2.aggregate[3], "aggregate statistics preserved")
        self.assertEqual(len(good_songs[0].comments), len(recover_good_songs[0].comments), "passing songs preserved")
        self.assertEqual(good_songs[0].comments[0], recover_good_songs[0].comments[0], "passing songs comments preserved")

