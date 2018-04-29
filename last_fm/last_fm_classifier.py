# Project Libraries
import last_fm_downloader as fm_dl
import feature_extraction as fe
import classifier as ml

# General Libraries


def extract_features(video_ids):
    video_ids_to_features = {}

    for video_id in video_ids:
        audio, sr = fe.get_audio(video_id)
        feats = fe.extract_features(audio, sr)
        video_ids_to_features[video_id] = feats

    return video_ids_to_features

def classify_examples(genre, video_ids_to_moods):
    positive_video_ids= []
    negative_video_ids = []

    for video_id, moods in video_ids_to_moods.items():
        if genre in moods:
            positive_video_ids.append(video_id)
        else:
            negative_video_ids.append(video_id)

    return positive_video_ids, negative_video_ids

def learn_classifier(video_ids_to_moods, genre):

    positive_video_ids, negative_video_ids = classify_examples(genre, video_ids_to_moods)

    video_ids = video_ids_to_moods.keys()
    print("Extracting Features...")
    video_ids_to_features = extract_features(video_ids)
    print("Done Extracting Features")

    positive_examples = [video_ids_to_features[video_id] for video_id in positive_video_ids]
    negative_examples = [video_ids_to_features[video_id] for video_id in negative_video_ids]

    positive_model, negative_model = ml.learn_classifier(positive_examples, negative_examples)

    print("\nResults for genre: %s" % genre)
    return positive_model, negative_model



moods = ['melodic', 'warm', 'anxious', 'romantic', 'dark']
limit = 10

# fm_dl.download_last_fm_data(moods, limit=limit)
video_ids_to_moods = fm_dl.load_video_id_dictionary(moods, limit)

learn_classifier(video_ids_to_moods, 'warm')

