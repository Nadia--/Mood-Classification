# Project Libraries
import filter as fltr
from song_aggregate import SongAggregateScraper
from five_million import random_songs

# General Libraries

MIN_NUM_COMMENTS = 40
MAX_NUM_COMMENTS = 100
NUM_SONGS = 100
FILTER_LIST = []

SAVEFILE = '5M_L100_MIN40_MAX100'

def scrape():

    video_ids = random_songs(NUM_SONGS)

    aggr = SongAggregateScraper()
    aggr.scrape_video_ids(video_ids, MIN_NUM_COMMENTS, MAX_NUM_COMMENTS, FILTER_LIST)
    aggr.print_summary()
    aggr.save_to_file(SAVEFILE)

def load_comments():
    aggr = SongAggregateScraper()
    aggr.load_from_file(SAVEFILE)
    passing_songs = aggr.get_passing_songs()
    #filter_list = [fltr.english_filter, fltr.length_filter, fltr.youtube_topics_filter]
    filter_list = [fltr.english_filter, fltr.length_filter, fltr.youtube_topics_filter, fltr.brutish_music_filter]

    print(len(passing_songs))

    for song in passing_songs:
        filtered_comments = fltr.run_filters(filter_list, song.comments)
        for idx, comment in enumerate(filtered_comments):
            print(idx, comment)

load_comments()