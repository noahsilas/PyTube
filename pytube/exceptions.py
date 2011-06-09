class AuthenticationError(Exception):
    """ Couldn't authenticate against the google auth API """


class CaptchaRequired(AuthenticationError):
    """ You must submit a captcha to continue """
    def __init__(self, data):
        self.url = data['Url']
        self.captcha = 'http://www.google.com/accounts/' + data['CaptchaUrl']
        self.token = data['CaptchaToken']
        self.solved = None


class TokenExpired(AuthenticationError):
    """ You are using an expired authentication token """


class VideoException(Exception):
    """ Failed to access a video """


class PrivateVideoException(VideoException):
    """ Tried to access a video that is marked as private """


class NoSuchVideoException(VideoException):
    """ Tried to access a video that does not exist or has been deleted """


class VideoUpdateException(VideoException):
    """ Failed to update a video """
