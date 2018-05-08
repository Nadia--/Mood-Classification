# Project Libraries
import filter as fltr

# General Libraries
import urllib.parse
import urllib.request
import json
from enum import Enum
import re

DEBUG = False

YOUTUBE_QUERY_URL = "https://www.googleapis.com/youtube/v3/"
YOUTUBE_SEARCH_URL = YOUTUBE_QUERY_URL + "search?"
YOUTUBE_VIDEOS_URL = YOUTUBE_QUERY_URL + "videos?"
YOUTUBE_COMMENTS_URL = YOUTUBE_QUERY_URL + "commentThreads?"

KEY = 'AIzaSyBAcQUU5I4FElmsYVK0irkDPVGQ_OLLkO0'  # TODO use key that isnt from stackoverflow XD


class FetchingError(Enum):
    ERROR_NO_RESULTS = "error: no video results"
    ERROR_NO_VIDEOID = "error: no videoId tag"
    ERROR_NO_COMMENTS = "error: no comments"
    ERROR_NO_TOKEN = "error: no next page token (probably not enough comments)"


def query(base, parameters):
    parameters['key'] = KEY
    url = base + urllib.parse.urlencode(parameters)
    json_result = urllib.request.urlopen(url).read().decode('utf-8')
    return json.loads(json_result)


class YouTubeSong:
    def __init__(self, artist=None, title=None, video_id=None):
        self.artist = artist
        self.title = title

        self.error = None
        self.youtube_title = None
        self.video_id = video_id
        self.comments = []

    def print_header(self, idx):
        print('%4d %s - %s' % (idx, self.artist, self.title))

    def obtain_comments(self, min_num_comments, max_num_comments, filter_list):
        if self.video_id is None:
            self.fetch_video_id()
        if self.error is None:
            self.fetch_youtube_comments(min_num_comments, max_num_comments, filter_list)

    def fetch_video_id(self):
        """
        Queries for YouTube video, populates video id
        """
        slist = query(YOUTUBE_SEARCH_URL, {'part': 'snippet', 'q': self.title + " " + self.artist})
        # print(json.dumps(slist['items'][0]['snippet'], indent=4, sort_keys=True))

        # Potential improvements:
        # 1. filter for "official music video" in title or description
        # 2. use more than one result
        chosen_result = 0
        if not slist['items']:
            self.set_error(FetchingError.ERROR_NO_RESULTS)
            return
        if 'videoId' not in slist['items'][chosen_result]['id']:
            self.set_error(FetchingError.ERROR_NO_VIDEOID)
            return
        self.video_id = slist['items'][chosen_result]['id']['videoId']
        self.youtube_title = slist['items'][chosen_result]['snippet']['title']

    def is_good_duration(self, lower_bound_sec, upper_bound_sec):
        """
        Returns whether the video duration is within specified bounds
        Expensive because requires another query, which consumes quota
        """
        try:
            metadata = query(YOUTUBE_VIDEOS_URL, {'id': self.video_id, 'part': 'contentDetails'})
            duration = metadata['items'][0]['contentDetails']['duration']
            dur = re.search('PT(\d+)M(\d+)S', duration)
            if not dur:
                self.set_error('error: duration is either seconds or hours long')
                return False

            minutes, seconds = map(int, re.search('PT(\d+)M(\d+)S', duration).groups())
            self.duration = minutes * 60 + seconds
            if self.duration < lower_bound_sec:
                self.set_error('error: duration is too short: %s minutes' % (self.duration / 60))
                return False
            if self.duration > upper_bound_sec:
                self.set_error('error: duration is too long: %s minutes' % (self.duration / 60))
                return False
            return True
        except:
            self.set_error('error: cannot parse duration query')
            return False

    def fetch_youtube_comments(self, min_num_comments, max_num_comments, filter_list):
        """
        Fetches comments, filters them, and analyzes them with vader, assuming video id has already been populated
        :param comment_count: the desired number of comments to fetch
        :param filter_list: the list of filters to impose on comments, while fetching them
        """

        # Obtain Comments
        next_page_token = None
        while 1:
            comments_parameters = {'part': 'snippet',
                                   'videoId': self.video_id,
                                   'maxResults': 100,
                                   'order': 'relevance'}
            if next_page_token is not None:
                comments_parameters['pageToken'] = next_page_token

            query_comments = query(YOUTUBE_COMMENTS_URL, comments_parameters)
            # print(json.dumps(query_comments, indent=4, sort_keys=True))

            comments = [x['snippet']['topLevelComment']['snippet']['textOriginal'] for x in query_comments['items']]
            if len(comments) == 0:
                self.set_error(FetchingError.ERROR_NO_COMMENTS)
                return

            # Filter Comments While Obtaining Them
            comments = fltr.run_filters(filter_list, comments)

            num_added = min(len(comments), max_num_comments - len(self.comments))
            self.comments += comments[:num_added]

            if len(self.comments) == max_num_comments:
                # Done
                break
            if 'nextPageToken' not in query_comments:
                if len(self.comments) < min_num_comments:
                    self.set_error(FetchingError.ERROR_NO_TOKEN)
                break
            next_page_token = query_comments['nextPageToken']

    def __str__(self):
        """ string representation of self """

        rep_str = '%s by %s\n\nvideo id: %s\nresults: %d' % (
            self.title, self.artist, self.video_id, len(self.comments))
        rep_str += '\n'

        return '\n' + rep_str + '\n'.join(self.comments) + '\n'

    def set_error(self, err):
        self.error = err
        if DEBUG:
            print(err)
