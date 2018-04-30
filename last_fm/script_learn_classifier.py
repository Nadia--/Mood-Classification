# Project Libraries
import last_fm_downloader as fm_dl
import last_fm_classifier as fm_cl

# General Libraries

def dummy_example():
    """ Dummy run on weakest/simplest parameters """
    moods = ['melodic', 'warm', 'anxious', 'romantic', 'dark']

    # fm_dl.download_last_fm_data(moods)
    video_ids_to_moods = fm_dl.load_video_id_to_moods(moods, 500)

    num_trials = 5
    num_components_variables = [1]
    covariance_type_variables = ['spherical']

    romantic_model = fm_cl.learn_classifier(video_ids_to_moods, 'romantic', 'romantic_feats_file_100', num_trials, num_components_variables, covariance_type_variables, limit=100)

    SONG_DIR = "./../data/youtube_data/songs/"
    song_name = 'Wait a Minute! - Willow Smith.mp3'

    is_romantic = fm_cl.predict_mood(SONG_DIR+song_name, romantic_model)

    if is_romantic:
        print("%s is romantic!" % song_name)
    else:
        print("%s is not romantic!" % song_name)


def robust_run():
    """ Run on several (still pretty weak/simple) parameters """
    moods = ['melodic', 'warm', 'anxious', 'romantic', 'dark']

    # fm_dl.download_last_fm_data(moods)
    video_ids_to_moods = fm_dl.load_video_id_to_moods(moods, 500)

    num_trials = 5
    num_components_variables = [1, 5, 10]
    covariance_type_variables = ['spherical', 'diag']

    romantic_model = fm_cl.learn_classifier(video_ids_to_moods, 'romantic', 'romantic_feats_file_100', num_trials, num_components_variables, covariance_type_variables, limit=100)

    SONG_DIR = "./../data/youtube_data/songs/"
    song_name = 'Wait a Minute! - Willow Smith.mp3'

    is_romantic = fm_cl.predict_mood(SONG_DIR+song_name, romantic_model)

    if is_romantic:
        print("%s is romantic!" % song_name)
    else:
        print("%s is not romantic!" % song_name)

robust_run()
