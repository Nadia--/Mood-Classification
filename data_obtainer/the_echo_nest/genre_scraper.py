# Project Libraries
import hdf5_helper as hh

# General Libraries
from enum import Enum
import sys

"""
API for scraping most commonly-occurring EchoNest descriptors in EchoNest data, including genre descriptors
"""

class WeightType(Enum):
    """
    Method with which to count descriptors:
    binary -- whether the descriptor appears in a song or not
    frequencies -- using the get_artist_term_frequencies data
    weights -- using the get_artist_terms_weights data
    """
    BINARY = "binary"
    FREQUENCY = "frequencies"
    WEIGHT = "weights"

def add_weights(dictionary, terms, weights=None):
    """
    Adds terms to the dictionary and augments their counts with respective weights
    """
    for idx, term in enumerate(terms):
        if weights is not None:
            if term in dictionary:
                dictionary[term] += weights[idx]
            else:
                dictionary[term] = weights[idx]

        else:
            if term in dictionary:
                dictionary[term] += 1
            else:
                dictionary[term] = 1

def sorted_array(dictionary):
    """
    Takes in a dictionary with descriptors mapped to their counts and
    returns an array of tuples (descriptor, count) sorted by highest count first
    """
    tuples = [(term, count) for term, count in dictionary.items()]
    tuples.sort(key=lambda x: x[1], reverse=True)
    return tuples

def scrape_genres(basedir, weightType, limit=None):
    """
    Scrapes a directory of TheEchoNest songs and compiles a list of most commonly-occurring song descriptors
    :param basedir: the directory to scrape
    :param weightType: WeightType enum for method to determine counts
    :param limit: the maximum number of songs within the directory that should be scraped
    :return: returns a sorted array of tuples of (descriptor, count) sorted by highest count first
    """
    songs = hh.get_all_files(basedir)
    if limit:
        songs = songs[:limit]
    print("Scraping %d songs" % len(songs))

    tags_counts = {}

    for song_loc in songs:
        h5 = hh.open_h5_file_read(song_loc)

        artist_tags = [term.decode('utf-8') for term in hh.get_artist_terms(h5)]

        if weightType == WeightType.BINARY:
            add_weights(tags_counts, artist_tags)

        elif weightType == WeightType.FREQUENCY:
            artist_tags_freqs = hh.get_artist_terms_freq(h5)
            add_weights(tags_counts, artist_tags, artist_tags_freqs)

        elif weightType == WeightType.WEIGHT:
            artist_tags_weights = hh.get_artist_terms_weight(h5)
            add_weights(tags_counts, artist_tags, artist_tags_weights)

        else:
            sys.exit("bad WeightType specified")

        h5.close()

    sorted_tags = sorted_array(tags_counts)
    return sorted_tags


