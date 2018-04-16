# Project Libraries
import filter as fltr
from song_aggregate import SongAggregateScraper
from five_million import random_songs

# General Libraries

""" Scrapes comments from a subset of 5 million YouTube song dataset """

MIN_NUM_COMMENTS = 40
MAX_NUM_COMMENTS = 80
NUM_SONGS = 100
filter_list = [fltr.english_filter]

video_ids = random_songs(NUM_SONGS)

aggr = SongAggregateScraper()
aggr.scrape_video_ids(video_ids, MIN_NUM_COMMENTS, MAX_NUM_COMMENTS, filter_list)
aggr.print_summary()

