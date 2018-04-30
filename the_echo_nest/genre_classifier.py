# Project Libraries
import hdf5_helper as hh
import classifier as ml

# General Libraries

"""
API for creating a binary classifier for a specific genre using MFCCs from TheEchoNest song data
"""

def scrape_songs_by_genre(basedir, genre, limit):
    """
    Returns the mfccs of songs that are in the genre, and outside of the genre

    :param basedir: the directory of songs we should classify
    :param genre: the genre we are looking to classify
    :param limit: the maximum number of songs within the directory that should be classified
    :return: mffcs of songs in the genre, mfccs of songs not in the genre
    """
    songs = hh.get_all_files(basedir)
    if limit:
        songs = songs[:limit]
    print("\n\nScraping %d songs for genre: %s" % (len(songs), genre))

    positive_examples = []
    negative_examples = []

    for song_loc in songs:
        h5 = hh.open_h5_file_read(song_loc)

        artist_tags = [term.decode('utf-8') for term in hh.get_artist_terms(h5)]
        almost_mfccs = hh.get_segments_timbre(h5)
        if genre in artist_tags:
            positive_examples.append(almost_mfccs)
        else:
            negative_examples.append(almost_mfccs)

        h5.close()

    return positive_examples, negative_examples


def learn_classifier(basedir, genre, split=0.5, num_trials=1, num_components=5, covariance_type='full', limit=None):
    """
    Divides up to limit songs in basedir by belonging to a genre or not
    Runs up to num_trials of creating and evaluating a classifier for those songs and prints average accuracy
    Returns the classifier with the best accuracy on test data

    :param basedir: the directory of songs we should classify
    :param genre: the genre we are looking to classify
    :param split: percent split in training vs testing data
    :param num_trials: the number of trials to run
    :param num_components: number of components in the gaussian mixture model
    :param covariance_type: the type of covariance in the gaussian mixture model
    :param limit: the maximum number of songs within the directory that should be classified
    """
    positive_examples, negative_examples = scrape_songs_by_genre(basedir, genre, limit)
    positive_model, negative_model, accuracy = \
        ml.learn_classifier(positive_examples, negative_examples, split, num_trials, num_components, covariance_type)

    print("\nResults for genre: %s" % genre)

    return positive_model, negative_model


