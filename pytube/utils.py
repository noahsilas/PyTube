import datetime
import urlparse

def yt_ts_to_datetime(yt_ts):
    """ Converts a youtube timestamp into a python datetime object.

        Note that these datetimes are PST or PDT.
        TODO: Figure out a reasonable way to handle timezone data.
    """
    dt = datetime.datetime.strptime(yt_ts[:19], '%Y-%m-%dT%H:%M:%S')
    dt = dt.replace(microsecond=int(yt_ts[20:22]))
    return dt


def video_id_from_youtube_url(url):
    """ Transforms a youtube url into the youtube video id.

        Supports the following url styles:
            - http://youtube.com/watch?v=<video_id>&weird=flags
            - http://youtu.be/<video_id>
    """
    parts = urlparse.urlparse(url)

    if parts.netloc == 'youtu.be':
        # return the path (minus the leading slash)
       return parts.path[1:]

    if 'youtube.com' not in parts.netloc:
        raise ValueError("Not a youtube video")
    try:
        return urlparse.parse_qs(parts.query)['v'][0]
    except KeyError:
        raise ValueError("Not a youtube video")
