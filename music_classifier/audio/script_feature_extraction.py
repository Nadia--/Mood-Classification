# Project Libraries
import feature_extraction as fe

# General Libraries

video_ids = ['lIYCHbOTab4', 'yzTuBuRdAyA']


audio, sr = fe.get_audio('lIYCHbOTab4')

result = fe.extract_features(audio, sr)
print(result.shape)

result2 = fe.extract_features(audio, sr, mfcc=False)
print(result2.shape)

