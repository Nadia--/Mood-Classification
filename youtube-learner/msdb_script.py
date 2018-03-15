# General Libraries

# Project Libraries
import hdf5_helper as hh

BASEDIR = '../../../data_sample/W/D/I'

songs = hh.get_all_files(BASEDIR)

songs = songs[:10]

for idx, song_loc in enumerate(songs):
    # Most of this music processing is done by TheEchoNest

    # Provides id on many different sites, so probably possible to retrieve exact audio file

    h5 = hh.open_h5_file_read(song_loc)
    artist = hh.get_artist_name(h5).decode('UTF-8')
    title = hh.get_title(h5).decode('UTF-8')
    year = hh.get_year(h5)
    dur = hh.get_duration(h5) # TODO: use this for duration-checking of youtube video, if willing to do extra query
    print("\n\nartist: %s, title: %s, year: %d, dur: %.1f" % (artist, title, year, dur))
    song_hotness = hh.get_song_hotttnesss(h5)
    artist_hotness = hh.get_artist_hotttnesss(h5)
    print('hotness song: %.2f, artist: %.2f' % (song_hotness, artist_hotness))

    key = hh.get_key(h5)
    key_conf = hh.get_key_confidence(h5)
    mode = hh.get_mode(h5)
    mode_conf = hh.get_mode_confidence(h5)
    tempo = hh.get_tempo(h5)
    time_sig = hh.get_time_signature(h5)
    ts_conf = hh.get_time_signature_confidence(h5)
    print('key: %d (%.2f), mode: %d (%.2f), tempo: %d, time sig: %d (%.2f)'
          % (key, key_conf, mode, mode_conf, tempo, time_sig, ts_conf))

    danceability = hh.get_danceability(h5)
    energy = hh.get_energy(h5)
    print('danceability: %.2f, energy: %.2f' % (danceability, energy))

    # to use these would have to use exact recording (not youtube one)
    tatums = hh.get_tatums_start(h5) # no idea what a tatum is...
    hh.get_tatums_confidence(h5)

    segments = hh.get_segments_start(h5)
    hh.get_segments_confidence(h5)

    sections = hh.get_sections_start(h5)
    hh.get_sections_confidence(h5)

    bars = hh.get_bars_start(h5) # time location of the start of every bar
    hh.get_bars_confidence(h5) # confidence of the value of the start of every bar

    beats = hh.get_beats_start(h5)
    hh.get_beats_confidence(h5)

    print('tatums: %d, segments: %d, sections: %d, bars: %d, beats: %d' %
          (len(tatums), len(segments), len(sections), len(bars), len(beats)))

    # the most detailed musical information
    hh.get_segments_pitches(h5) # 12 pitches
    hh.get_segments_timbre(h5) # MFCC mel frequency cepstrum coefficients


    artist_terms = hh.get_artist_terms(h5) # kind of like genres or descriptors (EchoNest)
    print('\nartist terms: %s' % str(artist_terms))
    artist_mbtags = hh.get_artist_mbtags(h5) # seems like another descriptor list (musicbrainz.org)
    print('artist mbtags: %s' % str(artist_mbtags))


    h5.close()


    """
    Features for Machine Learning:
    hotness (not always filled out :c)
    duration?
    tempo
    key 
    mode 
    num_sections
    timbre???? of each section ?
    pitches???? of each section ? ???? ???? ¿¿¿¿¿¿¿
    """
