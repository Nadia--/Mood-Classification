# Project Libraries
import objects as Objects
import filters as fltr
import hdf5_helper as hh

BASEDIR = '../../../data_sample/W/D'
NUM_COMMENTS = 100

songs = hh.get_all_files(BASEDIR)
print('Testing %d songs' % len(songs))

filter_tag_list = [fltr.english_filter]
aggr = Objects.SongsAggregate(NUM_COMMENTS, filter_tag_list, filt_songs=[])

songs = songs[0:10]

for idx, song_loc in enumerate(songs):
    song = Objects.Song(song_loc, NUM_COMMENTS, filter_tag_list)
    song.print_header(idx)

    try:
        song.process_comments()
        aggr.add_song(song)

    except:
        #TODO: catch 403 error because it probably means i ran out of YouTube requests quota
        print('EXCEPTION occured with this piece, ignoring')
        aggr.add_exception()

aggr.print_summary(filter_tag_list)

filtered_songs = aggr.get_filtered_songs()

song_hotnesses = [song.get_song_hotness() for song in filtered_songs]
artist_hotnesses = [song.get_artist_hotness() for song in filtered_songs]
comment_sentiment = [song.average_vader_sentiment for song in filtered_songs]

print(song_hotnesses)
print(artist_hotnesses)
print(comment_sentiment)

# TODO: graph x: song_hotness, y: vader_sentiment
# TODO: graph x: artist_hotness, y: vader_sentiment
