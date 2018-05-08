# Project Libraries
import rate_my_music_downloader as fm_dl
import music_classifier as fm_cl

# General Libraries

def helper(num_components_variables, covariance_type_variables):
    moods = ['melodic', 'warm', 'anxious', 'romantic', 'dark']

    # fm_dl.download_last_fm_data(moods)
    video_ids_to_moods = fm_dl.load_video_id_to_moods(moods, 500)

    num_trials = 5

    romantic_model = fm_cl.learn_classifier(video_ids_to_moods, 'romantic', 'romantic_feats_file_100', num_trials, num_components_variables, covariance_type_variables, limit=100)

    SONG_DIR = "./../data/youtube_data/songs/"
    song_name = 'Wait a Minute! - Willow Smith.mp3'

    is_romantic = fm_cl.predict_mood(SONG_DIR+song_name, romantic_model)

    if is_romantic:
        print("\n%s is romantic!" % song_name)
    else:
        print("\n%s is not romantic!" % song_name)

def dummy_run():
    # Dummy Run
    num_components_variables = [1]
    covariance_type_variables = ['spherical']
    helper(num_components_variables, covariance_type_variables)

def real_run():
    # More Real Run
    num_components_variables = [1, 5, 10]
    covariance_type_variables = ['spherical', 'diag']
    helper(num_components_variables, covariance_type_variables)

def intense_run():
    # Good Run
    num_components_variables = [1, 3, 5, 8]
    covariance_type_variables = ['spherical', 'diag', 'tied']
    helper(num_components_variables, covariance_type_variables)


# intense_run()

fm_dl.download_last_fm_data(None, depth=2)

