# Project Libraries
import music_classifier as fm_cl
import feature_extraction as fe

# General Libraries

MUSIC_DATA_DIR = "./../../data/rate_my_music/"

tune_par = fm_cl.TuningParameters()

tune_par.stft = [fe.pSTFT(0.1, 0.25)]
tune_par.feat_comb = [fe.pFeats(True, True, True), fe.pFeats(True, True, False), fe.pFeats(True, False, False), fe.pFeats(False, True, True)]
tune_par.num_mfccs = [20]
tune_par.num_components = [1]
tune_par.covariance_type = ['spherical']

print(tune_par)

fm_cl.tune_classifier(MUSIC_DATA_DIR, 'all_moods-888-1', 'romantic', 'all_moods-888-1', tune_par, num_trials=10, limit=40)

fm_cl.tune_classifier(MUSIC_DATA_DIR, 'all_moods-888-1', 'dark', 'all_moods-888-1', tune_par, num_trials=10, limit=40)

fm_cl.tune_classifier(MUSIC_DATA_DIR, 'all_moods-888-1', 'anxious', 'all_moods-888-1', tune_par, num_trials=10, limit=40)

fm_cl.tune_classifier(MUSIC_DATA_DIR, 'all_moods-888-1', 'warm', 'all_moods-888-1', tune_par, num_trials=10, limit=40)

fm_cl.tune_classifier(MUSIC_DATA_DIR, 'all_moods-888-1', 'melodic', 'all_moods-888-1', tune_par, num_trials=10, limit=40)

fm_cl.tune_classifier(MUSIC_DATA_DIR, 'all_moods-888-1', 'energetic', 'all_moods-888-1', tune_par, num_trials=10, limit=40)

fm_cl.tune_classifier(MUSIC_DATA_DIR, 'all_moods-888-1', 'melancholic', 'all_moods-888-1', tune_par, num_trials=10, limit=40)

fm_cl.tune_classifier(MUSIC_DATA_DIR, 'all_moods-888-1', 'hypnotic', 'all_moods-888-1', tune_par, num_trials=10, limit=40)

fm_cl.tune_classifier(MUSIC_DATA_DIR, 'all_moods-888-1', 'ethereal', 'all_moods-888-1', tune_par, num_trials=10, limit=40)

fm_cl.tune_classifier(MUSIC_DATA_DIR, 'all_moods-888-1', 'heavy', 'all_moods-888-1', tune_par, num_trials=10, limit=40)


