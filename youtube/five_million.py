# Project Libraries

# General Libraries
import glob
import numpy as np

"""
API for extracting a random subset of video_ids from the 5 Million YouTube songs dataset
"""

# Data from https://github.com/keunwoochoi/YouTube-music-video-5M

BASE_DIRECTORY = "./../data/youtube_data/5m_list/youtube_ids/"
FILE_PREFIX = 'youtube_video_ids_'
NUM_STORED_SONGS = 5119955


def is_artist_line(line):
    return line.startswith("# new artist:")

def get_textfile_name(file_num):
    """ returns dataset file name based on file number """
    fileglob = BASE_DIRECTORY + FILE_PREFIX + ("%02d_*.txt" % file_num)
    return glob.glob(fileglob)[0]


def regenereate_artists():
    """ creates a list of all artists from dataset and saves it to artists.txt """
    savefile = open(BASE_DIRECTORY + "artists.txt", "w+")

    fullglob = BASE_DIRECTORY + FILE_PREFIX + "*.txt"
    for textfile in glob.glob(fullglob):
        with open(textfile, 'r') as f:
            for line in f:
                if is_artist_line(line):
                    print(line)
                    savefile.write(line)


def determine_locations():
    """ an array with tuples corresponding to the location of every song: (file number, song number within file) """
    locations = [0] * NUM_STORED_SONGS

    pointer = 0
    for file_num in range(21):
        textfile = get_textfile_name(file_num)
        num_songs = int(textfile[-10:-4])

        for song_num in range(num_songs):
            locations[pointer + song_num] = (file_num, song_num)
        pointer += num_songs

    return locations


def random_songs(num_songs, seed=0):
    """
    Returns a random list of video_ids from the 5 million YouTube song dataset
    :param num_songs: the number of video ids to return
    :param seed: the seed to use for the randomization
    """
    print('Obtaining %d Random Video Ids' % num_songs)

    np.random.seed(seed)
    perms = [i for i in range(NUM_STORED_SONGS)]
    np.random.shuffle(perms)

    locations = determine_locations()
    video_ids = [0] * num_songs

    for i in range(num_songs):
        total_song_num = perms[i]
        file_num, song_num = locations[total_song_num]
        textfile = get_textfile_name(file_num)

        fp = open(textfile, "r")
        counter = 0
        for line in fp:
            if not is_artist_line(line):
                if counter == song_num:
                    video_ids[i] = line[:-1]
                    break
                counter += 1
        fp.close()

    return video_ids

