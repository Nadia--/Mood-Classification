# General Libraries
import re
from enum import Enum
import logging

# Project Libraries


LISTS_DIRECTORY = "./../word-lists/"

class Action(Enum):
    KEEP = 'keep'
    REMOVE = 'remove'
    REMOVE_EXCEPT = 'remove_except'
    FILTER_BY_NUM_LIKES = 'likes'
    FILTER_BY_LENGTH = 'length'
    REMOVE_VADER_0 = 'vader_0'

def list_from_file(filename, min_length=None):
    f = open(LISTS_DIRECTORY+filename, "r")
    words = set(f.read().split())
    if min_length is not None:
        assert(isinstance(min_length, int))
        words = set([word for word in words if len(word) > min_length])

    return words

def run_filters(filter_list, comments):
    """ Runs a list of filters in the order they appear on set of comments, returns filtered comments """
    for filt in filter_list:
        comments = filt.filter_comments(comments)
    return comments

class Filter:
    def __init__(self, name, action, key_words=None, cutoff_lb=None, cutoff_ub=None, min_num_likes=None):
        self.name = name
        self.action = action
        self.regex_key_words = '|'.join(key_words)
        self.cutoff_lb = cutoff_lb
        self.cutoff_ub = cutoff_ub
        self.min_num_likes = min_num_likes

    def __repr__(self):
        return self.name

    def filter_comments(self, comments):
        # TODO: turn this into a dictionary or something
        if self.action == Action.KEEP:
            return self.filter_keep(comments)
        elif self.action == Action.REMOVE:
            return self.filter_remove(comments)
        elif self.action == Action.REMOVE_EXCEPT:
            return self.filter_remove_except(comments)
        elif self.action == Action.FILTER_BY_NUM_LIKES and self.min_num_likes is not None:
            return self.filter_likes(comments)
        elif self.action == Action.FILTER_BY_LENGTH and (self.cutoff_lb is not None or self.cutoff_ub is not None):
            return self.filter_by_length(comments)
        elif self.action == Action.REMOVE_VADER_0:
            return self.filter_english_vader(comments)
        else:
            logging.ERROR('Filter of type action is not correctly configured')
            return comments


    def filter_remove(self, comments):
        return [comment for comment in comments if
                re.search(self.regex_key_words, comment.text, re.IGNORECASE) is None or comment.keep]

    def filter_remove_except(self, comments):
        return [comment for comment in comments if
                re.search(self.regex_key_words, comment.text, re.IGNORECASE) is not None or comment.keep]

    def filter_keep(self, comments):
        for comment in comments:
            match = re.search(self.regex_key_words, comment.text, re.IGNORECASE)
            if match:
                comment.keep = True
        return comments

    def filter_by_length(self, comments):
        if self.cutoff_ub is not None:
            comments = [comment for comment in comments
                if len(comment.text) <= self.cutoff_ub or comment.keep == True]
        if self.cutoff_lb is not None:
            comments = [comment for comment in comments
                        if len(comment.text) >= self.cutoff_lb or comment.keep == True]
        return comments

    def filter_likes(self, comments):
        return [comment for comment in comments
                if comment.like_count >= self.min_num_likes or comment.keep == True]

    def filter_english_vader(self, comments):
        return [comment for comment in comments if comment.vader_sentiment]

'''
""" Some Example Filters """
Example_Filters = [
      Filter(Action.KEEP, list_from_file('music_words'))
    , Filter(Action.REMOVE, ['setting', 'here'])
    # 'who's here from supernatural', 'lio rush brought me here'
    # 'if you change the setting to 1.5 speed it is slightly faster'
    , Filter(Action.REMOVE, ['Inhumans', 'Marvel', 'Lucifer'])
    , Filter(Action.REMOVE_EXCEPT, list_from_file('english_1000', 5))

    , Filter(Action.LIKES, min_num_likes=1)
    , Filter(Action.LENGTH, cutoff_ub=80)
    , Filter(Action.VADER_0)
]
'''

english_filter = Filter('english-1000-word-filter', Action.REMOVE_EXCEPT, list_from_file('english_1000', 5))
