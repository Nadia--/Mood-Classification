# Project Libraries

# General Libraries
import re
from enum import Enum
import logging

LISTS_DIRECTORY = "./../data/word_lists/"

class Action(Enum):
    REMOVE = 'remove'
    REMOVE_EXCEPT = 'remove_except'
    FILTER_BY_LENGTH = 'length'

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
    def __init__(self, name, action, key_words=None, cutoff_lb=None, cutoff_ub=None):
        self.name = name
        self.action = action
        self.regex_key_words = '|'.join(key_words)
        self.cutoff_lb = cutoff_lb
        self.cutoff_ub = cutoff_ub

    def __repr__(self):
        return self.name

    def filter_comments(self, comments):
        # TODO: turn this into a dictionary or something
        if self.action == Action.REMOVE:
            return self.filter_remove(comments)
        elif self.action == Action.REMOVE_EXCEPT:
            return self.filter_remove_except(comments)
        elif self.action == Action.FILTER_BY_LENGTH and (self.cutoff_lb is not None or self.cutoff_ub is not None):
            return self.filter_by_length(comments)
        else:
            logging.ERROR('Filter of type action is not correctly configured')
            return comments

    # TODO: add the ability to keep comments
    # TODO: add the ability to filter comments by number of likes

    def filter_remove(self, comments):
        return [comment for comment in comments if
                re.search(self.regex_key_words, comment, re.IGNORECASE) is None]

    def filter_remove_except(self, comments):
        return [comment for comment in comments if
                re.search(self.regex_key_words, comment, re.IGNORECASE) is not None]

    def filter_by_length(self, comments):
        if self.cutoff_ub is not None:
            comments = [comment for comment in comments
                        if len(comment) <= self.cutoff_ub]
        if self.cutoff_lb is not None:
            comments = [comment for comment in comments
                        if len(comment) >= self.cutoff_lb]
        return comments

'''
""" Some Example Filters """
Example_Filters = [
    , Filter(Action.REMOVE, ['setting', 'here'])
    # 'who's here from supernatural', 'lio rush brought me here'
    # 'if you change the setting to 1.5 speed it is slightly faster'
    , Filter(Action.REMOVE, ['Inhumans', 'Marvel', 'Lucifer'])
    , Filter(Action.REMOVE_EXCEPT, list_from_file('english_1000', 5))
    , Filter(Action.LENGTH, cutoff_ub=80)
]
'''

english_filter = Filter('english-1000-word-filter', Action.REMOVE_EXCEPT, list_from_file('english_1000', 5))
