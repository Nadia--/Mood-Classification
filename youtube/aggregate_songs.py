# Project Libraries
from youtube_song import FetchingError

# General Libraries
import logging

NUM_ERRORS = 6

class SongsAggregate:
    def __init__(self, min_num_comments, filter_tag_list, filt_songs=None):
        self.aggregate = [0]*NUM_ERRORS
        self.min_num_comments = min_num_comments
        self.filter_tag_list = filter_tag_list
        self.filt_songs = filt_songs

    def add_song(self, song):
        if song.error is None:
            print('     good')
            self.aggregate[0] +=1
            if self.filt_songs is not None:
                self.filt_songs.append(song)
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
        return self.filt_songs

    def percent_aggr(self, idx):
        return 100 * self.aggregate[idx] / sum(self.aggregate)

    def print_summary(self):
        print('\n\nSummary of Results \n')
        print('parameters: threshold usable comments: %d, filters: %s' % (self.min_num_comments, str(self.filter_tag_list)))
        print('total number of songs: %d\n' % sum(self.aggregate))

        print('%2d%% GOOD (%d total)\n' % (self.percent_aggr(0), self.aggregate[0]))

        print('%2d%% no comments (%d)' % (self.percent_aggr(3), self.aggregate[3]))
        print('%2d%% not enough comments (no next page token) (%d)' % (self.percent_aggr(4), self.aggregate[4]))
        print('%2d%% no video id (%d)' % (self.percent_aggr(2), self.aggregate[2]))
        print('%2d%% no video results (%d)' % (self.percent_aggr(1), self.aggregate[1]))
        print('%2d%% unhandled exceptions (%d)' % (self.percent_aggr(5), self.aggregate[5]))



