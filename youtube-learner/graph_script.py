# General Libraries
import math
import numpy as np
from matplotlib import pyplot as plt

# Project Libraries
import objects as Objects
import filters as fltr
import hdf5_helper as hh

BASEDIR = '../../../data_sample/W/D/'
MIN_NUM_COMMENTS = 30
MAX_NUM_COMMENTS = 200

songs = hh.get_all_files(BASEDIR)
songs = songs[:1000]
print('Testing %d songs' % len(songs))

filter_tag_list = [fltr.english_filter]
aggr = Objects.SongsAggregate(MIN_NUM_COMMENTS, filter_tag_list, filt_songs=[])

for idx, song_loc in enumerate(songs):
    song = Objects.Song(song_loc, MIN_NUM_COMMENTS, MAX_NUM_COMMENTS, filter_tag_list)
    song.print_header(idx)

    try:
        song.process_comments()
        aggr.add_song(song)

    except:
        #TODO: catch 403 error because it probably means i ran out of YouTube requests quota
        print('EXCEPTION occured with this piece, ignoring')
        aggr.add_exception()

aggr.print_summary()

filtered_songs = aggr.get_filtered_songs()
with_song_hotness = [song for song in filtered_songs if not math.isnan(song.get_song_hotness())]
with_artist_hotness = [song for song in filtered_songs if not math.isnan(song.get_artist_hotness())]

def plot(songs, is_song_hotness=True):
    if is_song_hotness:
        x_axis = [song.get_song_hotness() for song in songs]
    else:
        x_axis = [song.get_artist_hotness() for song in songs]
    y_axis = [song.average_vader_sentiment for song in songs]

    # Sort by the X axis
    data = [(x_axis[idx], y_axis[idx]) for idx, value in enumerate(x_axis)]
    data.sort(key=lambda x: x[0])
    x_axis = [pair[0] for pair in data]
    y_axis = [pair[1] for pair in data]

    plt.scatter(x_axis, y_axis)
    z = np.polyfit(x_axis, y_axis, 1)
    trendline = np.poly1d(z)
    plt.plot([0,1], trendline([0,1]))

    if is_song_hotness:
        plt.xlabel('EchoNest Song Hotness')
        plt.title('EchoNest Song Hotness vs YouTube Comments Sentiment')
    else:
        plt.xlabel('EchoNest Artist Hotness')
        plt.title('EchoNest Artist Hotness vs YouTube Comments Sentiment')
    plt.ylabel('YouTube Comments Sentiment')
    plt.xlim([0,1])
    plt.ylim([0,1])
    plt.show()

plot(with_song_hotness, is_song_hotness=True)
plot(with_artist_hotness, is_song_hotness=False)

