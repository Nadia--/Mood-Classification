# Project Libraries
from youtube_song import FetchingError
from youtube_song import YouTubeSong
import hdf5_helper as hh

# General Libraries
import json
import jsonpickle
import logging

CACHE_DIRECTORY = "./../data/youtube_data/comments/"
NUM_ERRORS = 6

class SongAggregateScraper:
    def __init__(self):
        # Parameter Metadata
        self.basedir = None
        self.video_ids = None
        self.limit = None
        self.min_num_comments = None
        self.max_num_comments = None
        self.filter_list = None
        self.save_filtered = None

        # Data Storage
        self.aggregate = None
        self.passing_songs = None

    def scrape_video_ids(self, video_ids, min_num_comments, max_num_comments, filter_list, save_filtered=True):
        """
        Scrape YouTubeSong comments from YouTube songs that correspond to list of video_ids

        :param video_ids: the YouTube video ids to scrape_from_echonest
        :param min_num_comments: the min number of comments for a YouTubeSong
        :param max_num_comments: the max number of comments for a YouTubeSong
        :param filter_list: the list of filters to run on the comments, while fetching them
        :param limit: a max number of songs (within directory) to scrape_from_echonest
        :param save_filtered: boolean - whether to save passing songs in an array or not
        """
        # Parameter Metadata
        self.video_ids = video_ids
        self.min_num_comments = min_num_comments
        self.max_num_comments = max_num_comments
        self.filter_list = filter_list
        self.save_filtered = save_filtered

        # Data Storage
        self.aggregate = [0]*NUM_ERRORS
        self.passing_songs = []

        self.start_video_id_scrape()

    def start_video_id_scrape(self):
        """ Runs through YouTube video ids and scrapes their comments """

        print('Scraping %d youtube songs' % len(self.video_ids))

        for idx, video_id in enumerate(self.video_ids):
            song = YouTubeSong(video_id=video_id)

            try:
                song.print_header(idx)
                song.obtain_comments(self.min_num_comments, self.min_num_comments, self.filter_list)
                self.add(song)

            except:
                # TODO: catch 403 error because it probably means i ran out of YouTube requests quota
                print('     EXCEPTION occurred with this piece, ignoring')
                self.add_exception()


    def scrape_from_echonest(self, basedir, min_num_comments, max_num_comments, filter_list, limit=None, save_filtered=True):
        """
        Scrape YouTubeSong comments from YouTube songs that correspond to TheEchoNest songs

        :param basedir: the directory of TheEchoNest data to scrape_from_echonest
        :param min_num_comments: the min number of comments for a YouTubeSong
        :param max_num_comments: the max number of comments for a YouTubeSong
        :param filter_list: the list of filters to run on the comments, while fetching them
        :param limit: a max number of songs (within directory) to scrape_from_echonest
        :param save_filtered: boolean - whether to save passing songs in an array or not
        """
        # Parameter Metadata
        self.basedir = basedir
        self.limit = limit
        self.min_num_comments = min_num_comments
        self.max_num_comments = max_num_comments
        self.filter_list = filter_list
        self.save_filtered = save_filtered

        # Data Storage
        self.aggregate = [0]*NUM_ERRORS
        self.passing_songs = []

        self.start_echonest_scrape()

    def start_echonest_scrape(self):
        """ Runs through EchoNest song data, extracts artist name and title, searches YouTube, and extracts comments """
        songs = hh.get_all_files(self.basedir)
        if self.limit:
            songs = songs[:self.limit]
        self.limit = len(songs)
        print('Scraping %d youtube songs' % len(songs))

        for idx, song_loc in enumerate(songs):
            h5 = hh.open_h5_file_read(song_loc)
            artist = hh.get_artist_name(h5).decode('utf-8')
            title = hh.get_title(h5).decode('utf-8')
            song = YouTubeSong(artist, title)

            try:
                song.print_header(idx)
                song.obtain_comments(self.min_num_comments, self.min_num_comments, self.filter_list)
                self.add(song)

            except:
                # TODO: catch 403 error because it probably means i ran out of YouTube requests quota
                print('     EXCEPTION occurred with this piece, ignoring')
                self.add_exception()

            h5.close()

    def load_from_file(self, filename):
        """ Loads an instance of self from filename """
        with open(CACHE_DIRECTORY+filename, "r") as savefile:
            saved_self = jsonpickle.decode(json.load(savefile))
            self.__dict__.update(saved_self.__dict__)

    def save_to_file(self, filename):
        """ Saves an instance of self in filename """
        with open(CACHE_DIRECTORY+filename, "w") as savefile:
            json.dump(jsonpickle.encode(self), savefile)

    def add(self, song):
        """ Adds song into aggregate statistics, and into self.passing_songs if it has sufficient comments """
        if song.error is None:
            print('     good')
            self.aggregate[0] +=1
            if self.save_filtered:
                self.passing_songs.append(song)
        else:
            print('     %s' % song.error)
            if song.error == FetchingError.ERROR_NO_RESULTS:
                self.aggregate[1] +=1
            elif song.error == FetchingError.ERROR_NO_VIDEOID:
                self.aggregate[2] +=1
            elif song.error == FetchingError.ERROR_NO_COMMENTS:
                self.aggregate[3] +=1
            elif song.error == FetchingError.ERROR_NO_TOKEN:
                self.aggregate[4] +=1
            else:
                logging.WARNING("unknown song error")
                # unknown error

    def add_exception(self):
        self.aggregate[5] += 1

    def get_passing_songs(self):
        return self.passing_songs

    def percent_aggr(self, idx):
        return 100 * self.aggregate[idx] / sum(self.aggregate)

    def print_summary(self):
        """ Prints aggregate statistics of the scrape """

        print('\n\nSummary of Results \n')
        print('parameters:')
        if self.basedir:
            print('num songs scraped: %d' % self.limit)
        else:
            print('num songs scraped: %d' % len(self.video_ids))
        print('min comments: %d' % self.min_num_comments)
        print('max comments: %d' % self.max_num_comments)
        print('filters: %s' % str(self.filter_list))

        print('\n%2d%% GOOD (%d total)\n' % (self.percent_aggr(0), self.aggregate[0]))

        print('%2d%% no comments (%d)' % (self.percent_aggr(3), self.aggregate[3]))
        print('%2d%% not enough comments (no next page token) (%d)' % (self.percent_aggr(4), self.aggregate[4]))
        print('%2d%% no video id (%d)' % (self.percent_aggr(2), self.aggregate[2]))
        print('%2d%% no video results (%d)' % (self.percent_aggr(1), self.aggregate[1]))
        print('%2d%% unhandled exceptions (%d)' % (self.percent_aggr(5), self.aggregate[5]))

