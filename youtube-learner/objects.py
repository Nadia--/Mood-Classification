# General Libraries
import urllib.request
import re
import json
import colored
from colored import stylize

# Project Libraries
import filters as Filters 

# https://github.com/cjhutto/vaderSentiment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

DEBUG = False
COLORS = False

YOUTUBE_QUERY_URL = "https://www.googleapis.com/youtube/v3/"
YOUTUBE_SEARCH_URL = YOUTUBE_QUERY_URL + "search?"
YOUTUBE_VIDEOS_URL = YOUTUBE_QUERY_URL + "videos?"
YOUTUBE_COMMENTS_URL = YOUTUBE_QUERY_URL + "commentThreads?"

KEY = 'AIzaSyBAcQUU5I4FElmsYVK0irkDPVGQ_OLLkO0' #TODO use key that isnt from stackoverflow XD

SENTIMENT_VADER = "vader"
SENTIMENT_USER = "user"

ERROR_NO_RESULTS = "error: no results"
ERROR_NO_VIDEOID = "error: no videoId tag"
ERROR_NO_COMMENTS = "error: no comments"
ERROR_NO_TOKEN = "error: no next page token (possibly not enough comments)"

def printd(arg, color=None):
    if DEBUG:
        if color is None or COLORS is False:
            print(arg)
        else:
            print(stylize(arg, colored.fg(color)))

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
    def __init__(self, artist, title): 
        self.error = None 
        self.artist = artist
        self.title = title
        self.youtube_title = None
        self.duration = None
        self.video_id = None
        self.comments = []
        self.average_vader_sentiment = None #TODO: add weights
        self.average_user_sentiment = None 


    # Populates artist, title, video_id, and comments
    def fetch_youtube_comments(self, comment_count, filter_tag_list):
        # Search for YouTube Video
        slist = query(YOUTUBE_SEARCH_URL, {'part':'snippet', 'q': self.title +" "+ self.artist})
        # print(json.dumps(slist['items'][0]['snippet'], indent=4, sort_keys=True))

        # Obtain YouTube Video ID
        # TODO: filter for legit link ("official music video" title or description)
        # TODO: use more than one result?
        # Currently choosing first result actually works pretty well 
        chosen_result = 0 #takes the first result
        if not slist['items']:
            self.debug(ERROR_NO_RESULTS, 'red')
            return
        if 'videoId' not in slist['items'][chosen_result]['id']:
            self.debug(ERROR_NO_VIDEOID, 'red')
            return
        self.video_id = slist['items'][chosen_result]['id']['videoId']
        self.youtube_title = slist['items'][chosen_result]['snippet']['title']
        #print(self.youtube_title)
        #print(self.video_id)

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
                self.debug(ERROR_NO_COMMENTS, 'red')
                return 
            for comment in comments:
                vs = vader.polarity_scores(comment.text)
                comment.vader_sentiment = vs['compound'] 

            # Filter Comments While Obtaining Them
            comments = Filters.run_filters(filter_tag_list, comments, self.title, self.artist)

            num_added = min(len(comments), comment_count)
            self.comments += comments[:num_added]
            comment_count -= num_added

            if comment_count <= 0:
                # Done
                break
            if 'nextPageToken' not in query_comments:
                self.debug(ERROR_NO_TOKEN, 'red')
                return 
            nextPageToken = query_comments['nextPageToken']

        # Check Duration of Video
        LB_SEC = 60 * 3
        UB_SEC = 60 * 7
        video_parameters = {'part': 'contentDetails', 'key': KEY}
        metadata = query(YOUTUBE_VIDEOS_URL, {'id': self.video_id, 'part': 'contentDetails'})
        duration = metadata['items'][0]['contentDetails']['duration']
        #print(duration)
        dur = re.search('\PT(\d+)M(\d+)S', duration)
        if not dur:
            self.debug('error: duration is either seconds or hours long', 'red')
            return
            
        minutes, seconds = map(int, re.search('\PT(\d+)M(\d+)S', duration).groups())
        self.duration = minutes * 60 + seconds
        if self.duration < LB_SEC: 
            self.debug('error: duration is too short: %s minutes' % (self.duration / 60), 'red')
            return
        if self.duration > UB_SEC:
            self.debug('error: duration is too long: %s minutes' % (self.duration / 60), 'red')
            return


    # Populates chosen sentiment
    def analyze_sentiment(self, classifier):
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

    # How to Represent Self
    def __str__(self):
        pairs = [str(comment) for comment in self.comments]

        rep_str = '%s by %s\n\nvideo id: %s\nresults: %d' % (
                self.title, self.artist, self.video_id, len(self.comments))
        if self.average_vader_sentiment is not None:
            rep_str+= '\nvader sentiment: %+.5f' % self.average_vader_sentiment
        if self.average_user_sentiment is not None:
            rep_str+= '\nuser sentiment: %+5f' % self.average_user_sentiment
        rep_str+='\n'


        return '\n' +rep_str + '\n'.join(pairs) + '\n'

    # debug helper function
    def debug(self, err, color=None):
        self.error = err
        printd(err, color)


