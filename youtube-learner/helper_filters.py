directory = "./../word-lists/"

def list_from_file(filename, min_length=None):
    f = open(directory+filename, "r")
    words = set(f.read().split())
    if min_length is not None:
        assert(isinstance(min_length, int))
        words = set([word for word in words if len(word) > min_length])

    return words 
