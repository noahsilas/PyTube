class AuthenticationError(Exception):
    """ Couldn't authenticate against the google auth API """


class VideoException(Exception):
    """ Failed to access a video """


class PrivateVideoException(VideoException):
    """ Tried to access a video that is marked as private """


class NoSuchVideoException(VideoException):
    """ Tried to access a video that does not exist or has been deleted """