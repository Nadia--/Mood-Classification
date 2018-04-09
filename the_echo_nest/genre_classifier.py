# Project Libraries
import hdf5_helper as hh

# General Libraries
import numpy as np
import random
from sklearn import mixture


def scrape_songs_by_genre(basedir, genre, limit):
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


def shuffle_examples(examples):
    perms = [i for i in range(len(examples))]
    random.shuffle(perms)
    examples_shuffled = [examples[i] for i in perms]
    return examples_shuffled


def is_in_genre_prediction(positive_model, negative_model, example_mfccs):
    pos_log_prob = positive_model.score(example_mfccs)
    neg_log_prob = negative_model.score(example_mfccs)
    if pos_log_prob > neg_log_prob:
        return True
    else:
        return False

def evaluate_classifier(positive_model, negative_model, positive_data, negative_data):
    data = []
    data.extend(positive_data)
    data.extend(negative_data)

    num_positive = len(positive_data)

    results = np.zeros((2,2))
    for idx, song_mfccs in enumerate(data):
        is_in_genre = is_in_genre_prediction(positive_model, negative_model, song_mfccs)
        if idx < num_positive:
            if is_in_genre:
                results[0][0] += 1
            else:
                results[0][1] += 1
        else:
            if is_in_genre:
                results[1][0] += 1
            else:
                results[1][1] += 1

    print("Model Results: (row = real label, col = assigned label, order: positive, negative)")
    print(results)

    correct = np.sum([results[i][i] for i in range(len(results))])
    accuracy = correct / np.sum(results)
    print("Total Accuracy: %.2f" % accuracy)
    return accuracy


def run_trial(positive_examples, negative_examples, split, num_components, covariance_type):
    num_pos_training = round(split * len(positive_examples))
    num_neg_training = round(split * len(negative_examples))

    # Shuffle
    positive_examples_shuffled = shuffle_examples(positive_examples)
    negative_examples_shuffled = shuffle_examples(negative_examples)

    # Split Data into Training and Testing
    positive_training = positive_examples_shuffled[:num_pos_training]
    negative_training = negative_examples_shuffled[:num_neg_training]
    positive_testing = positive_examples_shuffled[num_pos_training:]
    negative_testing = negative_examples_shuffled[num_neg_training:]

    # Flattening Data
    positive_concatenated = [mfcc for song in positive_training for mfcc in song]
    negative_concatenated = [mfcc for song in negative_training for mfcc in song]

    # Training the Model
    positive_model = mixture.GaussianMixture(n_components=num_components, covariance_type=covariance_type)
    positive_model.fit(positive_concatenated)
    negative_model = mixture.GaussianMixture(n_components=num_components, covariance_type=covariance_type)
    negative_model.fit(negative_concatenated)

    # Evaluate on Training Data
    print("\nTraining Data Model Results")
    training_accuracy = evaluate_classifier(positive_model, negative_model, positive_training, negative_training)

    # Evaluate on Test Data
    print("\nTesting Data Model Results")
    testing_accuracy = evaluate_classifier(positive_model, negative_model, positive_testing, negative_testing)

    return positive_model, negative_model, training_accuracy, testing_accuracy


def learn_classifier(basedir, genre, split=0.5, num_trials=1, num_components=5, covariance_type='full', limit=None):
    positive_examples, negative_examples = scrape_songs_by_genre(basedir, genre, limit)

    avg_training_accuracy = 0
    avg_testing_accuracy = 0

    best_accuracy = 0
    best_positive_model = None
    best_negative_model = None

    for t in range(num_trials):
        print("\nTrial %d" % (t+1))
        positive_model, negative_model, training_accuracy, testing_accuracy \
            = run_trial(positive_examples, negative_examples, split, num_components, covariance_type)

        if testing_accuracy > best_accuracy:
            best_positive_model = positive_model
            best_negative_model = negative_model
            best_accuracy = testing_accuracy

        avg_training_accuracy += training_accuracy / num_trials
        avg_testing_accuracy += testing_accuracy / num_trials

    print("\nResults for genre: %s" % genre)
    print("Average Training Accuracy: %.2f" % avg_training_accuracy)
    print("Average Testing Accuracy: %.2f" % avg_testing_accuracy)

    return best_positive_model, best_negative_model


