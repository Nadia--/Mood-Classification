
# Project Libraries
import objects as Objects
import filters as fltr
import hdf5_helper as hh

BASEDIR = '../../../data_sample/W/D'
MIN_NUM_COMMENTS = 60
MAX_NUM_COMMENTS = 100

#TODO: FIX SCRIPT STALL ON AND QUOTA DRAIN on songs that are not english but have a lot of comments
#TODO: catch exception for out of quota
#TODO: save data to file so dont have to query constantly

#Intermediate Project -- this will be useful in future, and can be used as a fall-back
#TODO: use machine learning to classify muiscal genres (from most common tags) from MFCCs [Training]
#TODO: download YouTube songs and generate inhouse MFCC
#TODO: use the learned classifier to classify song into genres

#Ultimate Goal
#TODO: use comments and video from same platform, do own music processing to extract various musical features, do ML on comments (labels) vs features.
#TODO: extrapolate either
#TODO      -- if someone states a mood, what musical attributes are likely to be found in the piece
#TODO      -- if certain elements are found in the piece, what mood people will report
"""
Desired Features:
chords
chord progressions
timbre, instrumental composition
tempo
stacatto vs smooth
loudness variance (are there lots of sudden rests)
etc general texture things
"""

#Enhancements
#TODO: improve comment filters so as to make sure comments are ABOUT THE SONG (not other random things)
#TODO: improve vader weighting if we're still using vader (not all comments should have equal weighting)
#TODO: re-run hotness vs sentiment graphs

songs = hh.get_all_files(BASEDIR)
songs = songs[0:10]
print('Testing %d songs' % len(songs))

filter_tag_list_A = [fltr.english_filter]
aggrA = Objects.SongsAggregate(MIN_NUM_COMMENTS, filter_tag_list_A)
'''
filter_tag_list_B = [Filters.REMOVE_LONG,
                     Filters.REMOVE_IF_NO_LIKES,
                     Filters.REMOVE_DUMB_COMMENTS,
                     Filters.KEEP_TITLE_AND_ARTIST,
                     Filters.KEEP_SONG_RELATED,
                     Filters.REMOVE_MOVIE_RELATED]
filter_tag_list_B = [Filters.REMOVE_NONENGLISH_AND_IRRELEVANT]
'''

for idx, song_loc in enumerate(songs):
    songA = Objects.Song(song_loc, MIN_NUM_COMMENTS, MAX_NUM_COMMENTS, filter_tag_list_A)

    try:
        # A
        songA.print_header(idx)
        songA.process_comments()
        aggrA.add_song(songA)

        # B
        '''
        songB = Objects.Song(artist, title)
        process_song(songB, filter_tag_list_B, 'B', filt_songs)
        '''

    except:
        #TODO: catch 403 error because it probably means i ran out of YouTube requests quota
        print('EXCEPTION occured with this piece, ignoring')
        aggrA.add_exception()

aggrA.print_summary()
