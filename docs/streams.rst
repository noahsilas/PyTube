==============
PyTube Streams
==============

Most PyTube methods that return a collection of objects actually return a 
`Stream`. Streams have some nice properties:

*   Streams will perform the minimum number of API queries necessary to
    return all of the results you have requested.
*   For some common behaviors (iterating, fetching the first N objects) the
    stream can maintain an internal cache, allowing you to iterate the stream
    multiple times or fetch an instance from the stream without sending
    additional youtube API queries.

Use Streams like lists
======================
::

    videos = client.user_videos('BeyonceVEVO')

    # iterate across a stream
    for video in videos:
        print video.title

    # slice a stream
    new_videos = videos[:10]
    older_videos = videos[10:20]

    # get one item from a stream
    video = videos[7]


Streams can only retrieve 1000 results
======================================
Due to limitations in the youtube API, streams may only return the first 1000
results. This can lead to confusing behavior: when you ask a stream for its
length it returns the total number of items in the collection, not the number
of items that it will return.::

    >>> len(videos)
    5223
    >>> len(list(videos))
    1000
