===============
PyTube Overview
===============

PyTube is a pure python library for accessing the YouTube Data API.


Example
=======
Display the 50 most recent videos from the 'mahalobaking' user::

    import pytube
    client = pytube.Client('my-app-identifier')
    videos = client.user_videos('mahalobaking')
    for video in videos[:50]:
        sys.stdout.write('%s %s\n' % (video.id, video.title))


Fetching Videos
===============

Getting a Specific Video
------------------------
client.video(`video_id`)
    Gets the video with youtube id `video_id`. If the video id doesn't exist,
    or has been deleted, this will raise `pytube.NoSuchVideoException`. If the
    video is private and the client is not authenticated to a user with
    permission to see it, this will raise `pytube.PrivateVideoException`.


Getting Videos from a Channel
-----------------------------
client.user_videos(`username='default`)
    Returns a video stream of videos in `username`'s channel. If the client is
    authenticated, you may omit the username to get the authenticated user's
    stream.


Searching for Videos
--------------------

client.video_search(`q=None, **query`)
    Returns a VideoStream of videos matching the query parameters.
    You can perform a basic search very simply::

        vids = c.video_search('search terms')

    You can also pass any of the `parameters accepted by the gdata API`_::

        vids = c.video_search(
            category='cars|music',  # category is cars or music
            author='schmoyoho',     # in schmoyoho's channel
            orderby='published',    # ordered by published date
            safeSearch='strict',    # 'moderate' and 'none' are the other safe search options
        )

.. _parameters accepted by the gdata API: http://code.google.com/apis/youtube/2.0/reference.html#Query_parameter_definitions


Video objects
=============

Attributes
----------
Videos fetched from the API should have the following attributes available.

* id
* title
* author
* category
* category.label
* keywords
* published
* updated
* description
* duration
* aspect_ratio
* private   -   True if this is a private video, False otherwise
* access_control - a dictionary mapping 'actions' to 'permissions'

Possible Attributes
-------------------
The following attributes may not be set on video objects, depending on the
privacy settings on the video you have fetched.

* like_count
* dislike_count
* favorite_count
* view_count
* comment_count
* uploaded  - the datetime that the video was uploaded

Available Streams
-----------------
Depending on the youtube API result, any or all of the following streams may
be available on Video instances:

Video.`related_videos`
    A stream of videos that youtube believes are related to this video.

Video.`video_responses`
    A stream of videos that are video responses to this video.

Video.`comments`
    A stream of comments made on this video

Updating A Video
----------------
Videos owned by a user who has authenticated this client can be updated. To
update a video, you simply update it's attributes and then call 
Video.`update`(). The following attributes may be updated this way:

* title
* description
* category
* keywords
* access_control
* private