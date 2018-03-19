# General Libraries
import urllib.request
import re
import json

# Project Libraries
import filters as Filters 

# https://github.com/cjhutto/vaderSentiment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

DEBUG = False

YOUTUBE_QUERY_URL = "https://www.googleapis.com/youtube/v3/"
YOUTUBE_SEARCH_URL = YOUTUBE_QUERY_URL + "search?"
YOUTUBE_VIDEOS_URL = YOUTUBE_QUERY_URL + "videos?"
YOUTUBE_COMMENTS_URL = YOUTUBE_QUERY_URL + "commentThreads?"

KEY = 'AIzaSyBAcQUU5I4FElmsYVK0irkDPVGQ_OLLkO0' #TODO use key that isnt from stackoverflow XD

SENTIMENT_VADER = "vader"
SENTIMENT_USER = "user"

NUM_ERRORS = 7;
ERROR_NO_RESULTS = "error: no results"
ERROR_NO_VIDEOID = "error: no videoId tag"
ERROR_NO_COMMENTS = "error: no comments"
ERROR_NO_TOKEN = "error: no next page token (possibly not enough comments)"

class Comment:
    def __init__(self, comment, like_count):
        self.text = comment
        self.like_count = like_count
        self.keep = False
        self.vader_sentiment = None
        self.user_sentiment = None
        self.closeness = None # -1 = red, 0 = yellow, 1 = green

    def __str__(self):
        
        rep_str = '(L:%d, K:%d' %(self.like_count, self.keep)

        if self.vader_sentiment is not None:
            rep_str += ', SV:%+.3f' % self.vader_sentiment
        if self.user_sentiment is not None:
            rep_str += ', US:%+.3f' % self.user_sentiment
        if self.closeness is not None:
            if self.closeness == -1:
                rep_str += ', ' + stylize('B', colored.fg('red'))
            elif self.closeness == 0:
                rep_str += ', ' + stylize('O', colored.fg('yellow'))
            else: 
                rep_str += ', ' + stylize('G', colored.fg('green'))

        rep_str+= ', M:"%s")' % self.text[:60]
        return rep_str

def query(base, parameters):
    parameters['key'] = KEY
    url = base + urllib.parse.urlencode(parameters)
    json_result = urllib.request.urlopen(url).read().decode('utf-8')
    return json.loads(json_result)

class Song:
    def __init__(self, artist, title, NUM_COMMENTS, filter_list):
        """
        Obtains YouTube comments for specified song
        :param artist: song artist
        :param title: song title
        :param NUM_COMMENTS: number of comments to retrieve
        :param filter_list: filters to apply to comments
        """
        self.error = None 
        self.artist = artist
        self.title = title
        self.youtube_title = None
        self.duration = None
        self.video_id = None
        self.comments = []
        self.average_vader_sentiment = None #TODO: add weights
        self.average_user_sentiment = None

        self.fetch_video_id()
        if self.error is None:
           self.fetch_youtube_comments(NUM_COMMENTS, filter_list)
        if self.error is None:
           self.analyze_sentiment(SENTIMENT_VADER)


    def is_good_duration(self, lower_bound_sec, upper_bound_sec):
        """
        Returns whether the video duration is within specified bounds
        Expensive because requires another query, which consumes quota
        """
        metadata = query(YOUTUBE_VIDEOS_URL, {'id': self.video_id, 'part': 'contentDetails'})
        duration = metadata['items'][0]['contentDetails']['duration']
        dur = re.search('\PT(\d+)M(\d+)S', duration)
        if not dur:
            self.set_error('error: duration is either seconds or hours long')
            return False

        minutes, seconds = map(int, re.search('\PT(\d+)M(\d+)S', duration).groups())
        self.duration = minutes * 60 + seconds
        if self.duration < lower_bound_sec:
            self.set_error('error: duration is too short: %s minutes' % (self.duration / 60))
            return False
        if self.duration > upper_bound_sec:
            self.set_error('error: duration is too long: %s minutes' % (self.duration / 60))
            return False
        return True

    def fetch_video_id(self):
        """
        Queries for YouTube video, populates video id
        """
        slist = query(YOUTUBE_SEARCH_URL, {'part':'snippet', 'q': self.title +" "+ self.artist})
        # print(json.dumps(slist['items'][0]['snippet'], indent=4, sort_keys=True))

        # Obtain YouTube Video ID
        # TODO: filter for legit link ("official music video" title or description)
        # TODO: use more than one result?
        # Currently choosing first result actually works pretty well
        chosen_result = 0
        if not slist['items']:
            self.set_error(ERROR_NO_RESULTS)
            return
        if 'videoId' not in slist['items'][chosen_result]['id']:
            self.set_error(ERROR_NO_VIDEOID)
            return
        self.video_id = slist['items'][chosen_result]['id']['videoId']
        self.youtube_title = slist['items'][chosen_result]['snippet']['title']

    def fetch_youtube_comments(self, comment_count, filter_list):
        """
        Fetches comments, filters them, and analyzes them with vader, assuming video id has already been populated
        :param comment_count: the desired number of comments to fetch
        :param filter_list: the list of filters to impose on comments, while fetching them
        """
        vader = SentimentIntensityAnalyzer()

        # Obtain Comments
        nextPageToken = None
        while 1:
            comments_parameters = {'part': 'snippet', 
                    'videoId': self.video_id, 
                    'maxeesults': 100,
                    'order':'relevance'}
            if nextPageToken is not None:
                comments_parameters['pageToken'] = nextPageToken

            query_comments = query(YOUTUBE_COMMENTS_URL, comments_parameters)
            #print(json.dumps(query_comments, indent=4, sort_keys=True))

            comments = [Comment(
                x['snippet']['topLevelComment']['snippet']['textOriginal'], 
                x['snippet']['topLevelComment']['snippet']['likeCount']) 
                for x in query_comments['items']]
            if len(comments) == 0:
                self.set_error(ERROR_NO_COMMENTS)
                return 
            for comment in comments:
                vs = vader.polarity_scores(comment.text)
                comment.vader_sentiment = vs['compound'] 

            # Filter Comments While Obtaining Them
            comments = Filters.run_filters(filter_list, comments)

            num_added = min(len(comments), comment_count)
            self.comments += comments[:num_added]
            comment_count -= num_added

            if comment_count <= 0:
                # Done
                break
            if 'nextPageToken' not in query_comments:
                self.set_error(ERROR_NO_TOKEN)
                return 
            nextPageToken = query_comments['nextPageToken']


    def analyze_sentiment(self, classifier):
        """
        Updates comments and Song with sentiment
        :param classifier:
        """
        sentiment = 0.0;
        num_items = 0;
        for comment in self.comments:
            num_items+=1
            comment_sentiment = None
            if classifier == SENTIMENT_VADER:
                comment_sentiment = comment.vader_sentiment 
            if classifier == SENTIMENT_USER:
                print("comment: %s" % comment.text)
                comment_sentiment = float(input("Your rating? [-1,1] "))
                comment.user_sentiment = comment_sentiment
            sentiment += (comment_sentiment - sentiment) / num_items
        if classifier == SENTIMENT_VADER:
            self.average_vader_sentiment = sentiment
        if classifier == SENTIMENT_USER:
            self.average_user_sentiment = sentiment

    def compare_analysis(self):
        if self.average_user_sentiment is None or self.average_vader_sentiment is None:
            return
        for comment in self.comments:
            diff = abs(comment.vader_sentiment - comment.user_sentiment)
            if diff < 0.2:
                comment.closeness = 1
            elif diff < 0.5:
                comment.closeness = 0
            else: 
                comment.closeness = -1

    def __str__(self):
        """
        string representation of self
        """
        pairs = [str(comment) for comment in self.comments]

        rep_str = '%s by %s\n\nvideo id: %s\nresults: %d' % (
                self.title, self.artist, self.video_id, len(self.comments))
        if self.average_vader_sentiment is not None:
            rep_str+= '\nvader sentiment: %+.5f' % self.average_vader_sentiment
        if self.average_user_sentiment is not None:
            rep_str+= '\nuser sentiment: %+5f' % self.average_user_sentiment
        rep_str+='\n'

        return '\n' +rep_str + '\n'.join(pairs) + '\n'

    def set_error(self, err):
        self.error = err
        if DEBUG:
            print(err)

class SongsAggregate:
    def __init__(self, num_comments, filt_songs=None):
        self.aggregate = [0]*NUM_ERRORS
        self.num_comments = num_comments
        self.filt_songs = filt_songs

    def process_song(self, song):
        if song.error is None:
            print('     good')
            if len(song.comments) >= self.num_comments:
                self.aggregate[0] +=1
                if self.filt_songs is not None:
                    self.filt_songs.append(song)
        else:
            print('     %s' % song.error)
            if song.error == ERROR_NO_RESULTS:
                self.aggregate[1] +=1
            elif song.error == ERROR_NO_VIDEOID:
                self.aggregate[2] +=1
            elif song.error == ERROR_NO_COMMENTS:
                self.aggregate[3] +=1
            elif song.error == ERROR_NO_TOKEN:
                self.aggregate[4] +=1
            else:
                # assuming is a video duration error
                self.aggregate[5] +=1

    def add_exception(self):
        self.aggregate[6] += 1

    def percent_aggr(self, idx):
        return 100 * self.aggregate[idx] / sum(self.aggregate)

    def print_summary(self, filter_tag_list_A):
        print('\n\nSummary of Results \n')
        print('parameters: threshold usable comments: %d, filters: %s' % (self.num_comments, str(filter_tag_list_A)))
        print('total number of songs: %d\n' % sum(self.aggregate))

        print('%2d%% GOOD (%d total)\n' % (self.percent_aggr(0), self.aggregate[0]))

        print('%2d%% no comments (%d)' % (self.percent_aggr(3), self.aggregate[3]))
        print('%2d%% no next page token (%d)' % (self.percent_aggr(4), self.aggregate[4]))
        print('%2d%% unexpected duration (%d)' % (self.percent_aggr(5), self.aggregate[5]))
        print('%2d%% no video id (%d)' % (self.percent_aggr(2), self.aggregate[2]))
        print('%2d%% no video results (%d)' % (self.percent_aggr(1), self.aggregate[1]))
        print('%2d%% unhandled exceptions (%d)' % (self.percent_aggr(6), self.aggregate[6]))


