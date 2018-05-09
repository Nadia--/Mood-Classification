# Project Libraries
import music_classifier as fm_cl
import feature_extraction as fe

# General Libraries

MUSIC_DATA_DIR = "./../../data/rate_my_music/"

tune_par = fm_cl.TuningParameters()

tune_par.stft = [fe.pSTFT(0.05, 0.25), fe.pSTFT(0.1, 0.25), fe.pSTFT(0.15, 0.25)]
tune_par.feat_comb = [fe.pFeats(True, True, True)]
tune_par.num_mfccs = [20]
tune_par.num_components = [1]
tune_par.covariance_type = ['spherical']

print(tune_par)

fm_cl.tune_classifier(MUSIC_DATA_DIR, 'all_moods-888-1', 'romantic', 'all_moods-888-1', tune_par, num_trials=10, limit=20)
