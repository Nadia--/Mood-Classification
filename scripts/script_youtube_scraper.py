# Project Libraries
import filters as fltr
import hdf5_helper as hh
from aggregate_songs import SongsAggregate
from youtube_song import YouTubeSong

# General Libraries

BASEDIR = '../../../../Thesis/data_sample/W/D/I'
MIN_NUM_COMMENTS = 20
MAX_NUM_COMMENTS = 80

songs = hh.get_all_files(BASEDIR)
songs = songs[:10]
print('Testing %d songs' % len(songs))

filter_list = [fltr.english_filter]
aggr = SongsAggregate(MIN_NUM_COMMENTS, filter_list, [])

for idx, song_loc in enumerate(songs):
    h5 = hh.open_h5_file_read(song_loc)
    artist = hh.get_artist_name(h5).decode('utf-8')
    title = hh.get_title(h5).decode('utf-8')
    song = YouTubeSong(artist, title, MIN_NUM_COMMENTS, MAX_NUM_COMMENTS)

    try:
        song.print_header(idx)
        song.obtain_comments(filter_list)
        aggr.add_song(song)

    except:
        # TODO: catch 403 error because it probably means i ran out of YouTube requests quota
        print('     EXCEPTION occurred with this piece, ignoring')
        aggr.add_exception()

    h5.close()

aggr.print_summary()
