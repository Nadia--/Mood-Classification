# Project Libraries
import filter as fltr
from song_aggregate import SongAggregateScraper
from five_million import random_songs

# General Libraries

""" Scrapes comments from a subset of 5 million YouTube song dataset """

BASEDIR = '../../../../Thesis/data_sample/W/D'
MIN_NUM_COMMENTS = 40
MAX_NUM_COMMENTS = 80
NUM_SONGS = 100
filter_list = [fltr.english_filter]

video_ids = random_songs(NUM_SONGS)

aggr_5m = SongAggregateScraper()
aggr_5m.scrape_video_ids(video_ids, MIN_NUM_COMMENTS, MAX_NUM_COMMENTS, filter_list)

aggr_echo = SongAggregateScraper()
aggr_echo.scrape_from_echonest(BASEDIR, MIN_NUM_COMMENTS, MAX_NUM_COMMENTS, filter_list, limit=NUM_SONGS)

aggr_5m.print_summary()
aggr_echo.print_summary()
