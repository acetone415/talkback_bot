def load_tracklist(filename):
    """
    This function takes file with tracklist and returns:
     1) dict, where keys - authors, values - list of songs by author
     2) list of all songs
     """

    sep, tracklist_by_author, all_songs = '-', {}, []
    with open(filename) as f:
        for line in f:
            author_song = line.rstrip().split(sep=sep)  # read pair "author - song title"
            all_songs.append(author_song[1])
            if author_song[0] not in tracklist_by_author.keys():
                tracklist_by_author[author_song[0]] = [author_song[1]]  # author: [song1]
            else:
                tracklist_by_author[author_song[0]].append(author_song[1])  # author: [song1, ..., songN]
    return tracklist_by_author, all_songs

print(load_tracklist('test.txt'))