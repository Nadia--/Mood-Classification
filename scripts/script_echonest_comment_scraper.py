# Project Libraries
import filter as fltr
from song_aggregate import SongAggregateScraper

# General Libraries

""" Scrapes comments from a subset of TheEchoNest song dataset """

BASEDIR = '../../../../Thesis/data_sample/W/D/I'
MIN_NUM_COMMENTS = 10
MAX_NUM_COMMENTS = 80
limit = 10
filter_list = [fltr.english_filter]

aggr = SongAggregateScraper()
aggr.scrape_from_echonest(BASEDIR, MIN_NUM_COMMENTS, MAX_NUM_COMMENTS, filter_list, limit=limit)
aggr.print_summary()
aggr.save_to_file('WDI_L10_MIN10_MAX80_english')
good_songs = aggr.get_passing_songs()

aggr2 = SongAggregateScraper()
aggr2.load_from_file('WDI_L10_MIN10_MAX80_english')
aggr2.print_summary()
recover_good_songs = aggr2.get_passing_songs()

print(good_songs[0])
print(recover_good_songs[0])

