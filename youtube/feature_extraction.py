# Project Libraries

# General Libraries
import glob
import librosa

"""
API for extracting various features from audio tracks
Currently supporting: MFCCs
"""

BASE_DIRECTORY = "./../data/youtube_data/songs/"


def get_audiofile_name(video_id):
    """ Returns local audio file name based on its YouTube video id"""
    fileglob = BASE_DIRECTORY + ("%s.*.mp3" % video_id)
    return glob.glob(fileglob)[0]


def extract_mfccs(video_ids, num_mfccs=20):
    """ Extracts MFCCs from audio tracks corresponding to YouTube video ids"""
    mfccs = [0] * len(video_ids)

    for idx, video_id in enumerate(video_ids):
        audio_file = get_audiofile_name(video_id)
        print(audio_file)
        audio, sr = librosa.load(audio_file)
        mfccs[idx] = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=num_mfccs)

    return mfccs


mfccs = extract_mfccs(['lIYCHbOTab4', 'yzTuBuRdAyA'])
print(mfccs[0].shape)
