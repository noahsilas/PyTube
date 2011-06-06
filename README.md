PyTube
======
Pythonic bindings for the YouTube API.

Get Some Videos!
----------------
Display the 50 most recent video ids and titles from the Mahalo Baking channel

    import pytube
    client = pytube.Client('my-app-identifier')
    videos = client.user_videos('mahalobaking')
    for video in videos[:50]:
        sys.stdout.write('%s %s\n' % (video.id, video.title))

Streams are cached!
-------------------------
Streams try to do as few API queries as possible 

    vs = client.user_videos('mahalobaking')     # does not hit the YouTube API
    top_ten = vs[:10]                           # actually grabs the first page of results (50) from API
    first = vs[0]                               # returns instantly from local cache!


Motivation
----------

The gdata API obscures the data you are actually interested in; suppose that
you wanted to find out who was the author of a given video; you might write
a function like this:

gdata:

    import gdata.youtube.service
    def get_author(video_id):
        yt_service = gdata.youtube.service.YouTubeService()
        yt_service.source = 'my-example-application'
        entry = yt_service.GetYouTubeVideoEntry(video_id=video_id)
        return entry.author[0].name.text

pytube:

    import pytube
    def get_author(video_id)
        entry = pytube.Client('my-example-application').video(video_id)
        return entry.author


Introspecting a gdata entry isn't terribly helpful: All of the relevant
data is buried in deep levels of object hierarchy. PyTube tries to expose
as much data as possible in python native data structures. Try looking at
a video object's \_\_dict\_\_!


Planned Features
----------------
* OAuth Authentication Support

* Performing multiple API queries simultaneously for increased speed when
  iterating across large collections

* Support for Playlist Operations

Known Issues
------------

* WHERE ARE THE TESTS

* A video entry without a view_count may either have zero views or it may have it's statistics protected. (http://bit.ly/hWwk40)

* len(Stream) will return the total length of the stream (number of videos in a channel, number of search results, etc), but only the first 1000 of these results are iterable. This is a restriction of the YouTube API.

* video_id_from_youtube_url doesn't support channel urls (example: http://www.youtube.com/user/beyonceVEVO#p/u/0/4m1EFMoRFvY )

* Data objects contain references to their client; pickling a VideoStream will
  also pickle the associated client, which may inadvertently cause
  authentication tokens to be preserved.

* Dates from youtube are always returned as Pacific time (PST or PDT); there should be options for localizing based on time.timezone/time.altzone or converting to UTC

Authors
-------
Noah Silas (noah@mahalo.com)
Kai Powell (kai@mahalo.com)
