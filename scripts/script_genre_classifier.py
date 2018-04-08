# Project Libraries
from genre_classifier import learn_classifier

# General Libraries

BASEDIR = '../../../../Thesis/data_sample/W/D'
rock_positive_model, rock_negative_model = learn_classifier(BASEDIR, b'rock', num_trials=5, limit=200)
jazz_positive_model, jazz_negative_model = learn_classifier(BASEDIR, b'jazz', num_trials=5, limit=200)
