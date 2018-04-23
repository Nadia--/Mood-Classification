# Project Libraries

# General Libraries
import re
from enum import Enum
import logging

LISTS_DIRECTORY = "./../data/word_lists/"

class Action(Enum):
    """ The type of filter """
    REMOVE = 'remove'
    REMOVE_EXCEPT = 'remove_except'
    SUBSTRING_MATCH = 'substring_match'
    FILTER_BY_LENGTH = 'length'

def list_from_file(filename, min_length=None):
    """ returns a set of words from a local file containing said words """
    f = open(LISTS_DIRECTORY+filename, "r")
    words = set(f.read().split())
    if min_length is not None:
        assert(isinstance(min_length, int))
        words = set([word for word in words if len(word) >= min_length])

    return words

def run_filters(filter_list, comments):
    """ Runs a list of filters in the order they appear on set of comments, returns filtered comments """
    for filt in filter_list:
        comments = filt.filter_comments(comments)
    return comments

class Filter:
    def __init__(self, name, action, key_words=None, cutoff_lb=None, cutoff_ub=None):
        """ The declaration of the filter parameters """
        self.name = name
        self.action = action
        self.key_words = None
        if key_words:
            self.key_words = key_words
        self.cutoff_lb = cutoff_lb
        self.cutoff_ub = cutoff_ub

    def __repr__(self):
        return self.name

    def filter_comments(self, comments):
        """ Runs the filter on the comments, returns filtered comments """
        # TODO: turn this into a dictionary or something
        if self.action == Action.REMOVE:
            return self.filter_remove(comments)
        elif self.action == Action.REMOVE_EXCEPT:
            return self.filter_remove_except(comments)
        elif self.action == Action.SUBSTRING_MATCH:
            return self.filter_substring_match(comments)
        elif self.action == Action.FILTER_BY_LENGTH and (self.cutoff_lb is not None or self.cutoff_ub is not None):
            return self.filter_by_length(comments)
        else:
            logging.ERROR('Filter of type action is not correctly configured')
            return comments

    # TODO: add the ability to keep comments
    # TODO: add the ability to filter comments by number of likes

    def are_key_words_in_comment(self, comment):
        """ returns true if there are any filter key words in comment, (matches whole words only)"""
        comment_set = set(comment.lower().split())
        word_set = set(self.key_words)

        # print(comment_set)
        # intersection = set.intersection(comment_set, word_set)
        # print("common words:", intersection)

        return bool(comment_set & word_set)


    def filter_remove(self, comments):
        """ Removes comments with filter's key words """
        return [comment for comment in comments if not self.are_key_words_in_comment(comment)]

    def filter_remove_except(self, comments):
        """ Removes comments without filter's key words """
        return [comment for comment in comments if self.are_key_words_in_comment(comment)]

    def filter_substring_match(self, comments):
        """ Removes comments without filter's key words as substrings """
        return [comment for comment in comments
                if re.search('|'.join(self.key_words), comment, re.IGNORECASE) is not None]

    def filter_by_length(self, comments):
        """ Removes comments that are too short or too long """
        if self.cutoff_lb is not None:
            comments = [comment for comment in comments
                        if len(comment) >= self.cutoff_lb]
        if self.cutoff_ub is not None:
            comments = [comment for comment in comments
                        if len(comment) <= self.cutoff_ub]
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

english_filter = Filter('english-1000-word-filter', Action.REMOVE_EXCEPT, list_from_file('english_1000', 4))
avoid_negations_filter = Filter('avoid-negations-filter', Action.REMOVE, list_from_file('negations'))
length_filter = Filter('length-filter', Action.FILTER_BY_LENGTH, cutoff_lb=7, cutoff_ub=200)
youtube_topics_filter = Filter('youtube_topics_filter', Action.REMOVE, list_from_file('youtube_topics_and_fads'))

brutish_music_filter = Filter('brutish_filter', Action.SUBSTRING_MATCH, list_from_file('music_words') | list_from_file('mood_words'))
