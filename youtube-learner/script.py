
#Project Libraries
import objects as Objects
import filters as fltr
import hdf5_helper as hh

BASEDIR = '../../../data_sample/W/D'
NUM_COMMENTS = 60

#TODO: look at MSDB tags
#TODO: ML correlations between tags and comments

#TODO: improve comment filters to work really well
#TODO: improve vader weighting (not all comments should have equal weighting)

#Goals
#TODO: check for correlation between "hotness" and comments
#TODO: do mood classification on comments, check for correlation with chords, etc?

#Reach Goal
#TODO: stop using MSDB and use YouTube videos directly, do in house music processing

def process_song(song, char, filt_songs=None):
    if song.error is None:
        print('     good') 
        if len(song.comments) >= NUM_COMMENTS:
            if char == 'A' and filt_songs is not None:
                filt_songs.append(song)
                aggregate[0] +=1
    else:
        print('     %s' % song.error)
        if song.error == Objects.ERROR_NO_RESULTS:
            aggregate[1] +=1
        elif song.error == Objects.ERROR_NO_VIDEOID:
            aggregate[2] +=1
        elif song.error == Objects.ERROR_NO_COMMENTS:
            aggregate[3] +=1
        elif song.error == Objects.ERROR_NO_TOKEN:
            aggregate[4] +=1
        else:
            # assuming is a video duration error
            aggregate[5] +=1

songs = hh.get_all_files(BASEDIR)
print('Testing %d songs' % len(songs))
num_total = 0
filt_songs = []

aggregate = [0]*7

songs = songs[0:10]

for idx, song_loc in enumerate(songs):
    h5 = hh.open_h5_file_read(song_loc)
    artist = hh.get_artist_name(h5).decode('UTF-8')
    title = hh.get_title(h5).decode('UTF-8')
    print('%4d %s - %s' %(idx, artist, title))

    try:
        # A
        #filter_tag_list_A = []
        filter_tag_list_A = [fltr.english_filter]
        songA = Objects.Song(artist, title, NUM_COMMENTS, filter_tag_list_A)
        process_song(songA, 'A', filt_songs)

        # B
        '''
        songB = Objects.Song(artist, title)
        filter_tag_list_B = [Filters.REMOVE_LONG,
                Filters.REMOVE_IF_NO_LIKES, 
                Filters.REMOVE_DUMB_COMMENTS, 
                Filters.KEEP_TITLE_AND_ARTIST, 
                Filters.KEEP_SONG_RELATED, 
                Filters.REMOVE_MOVIE_RELATED]
        filter_tag_list_B = [Filters.REMOVE_NONENGLISH_AND_IRRELEVANT]
        process_song(songB, filter_tag_list_B, 'B', filt_songs)
        '''

        h5.close()
    except:
        #TODO: catch 403 error because it probably means i ran out of YouTube requests quota
        print('EXCEPTION occured with this piece, ignoring')
        aggregate[6] +=1


def percent_aggr(idx):
    return 100 * aggregate[idx] / sum(aggregate)

print('\n\nSummary of Results \n')
print('parameters: threshold usable comments: %d, filters: %s' % (NUM_COMMENTS, str(filter_tag_list_A)))
print('total number of songs: %d\n' % sum(aggregate))

print('%2d%% GOOD (%d total)\n' % (percent_aggr(0), aggregate[0]))

print('%2d%% no comments (%d)' % (percent_aggr(3), aggregate[3]))
print('%2d%% no next page token (%d)' % (percent_aggr(4), aggregate[4]))
print('%2d%% unexpected duration (%d)' % (percent_aggr(5), aggregate[5]))
print('%2d%% no video id (%d)' % (percent_aggr(2), aggregate[2]))
print('%2d%% no video results (%d)' % (percent_aggr(1), aggregate[1]))
print('%2d%% unhandled exceptions (%d)' % (percent_aggr(6), aggregate[6]))

