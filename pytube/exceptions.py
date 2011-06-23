class AuthenticationError(Exception):
    """ Couldn't authenticate against the google auth API """


class CaptchaRequired(AuthenticationError):
    """ You must submit a captcha to continue """
    def __init__(self, msg, data={}):
        self.url = data.get('Url', '')
        self.captcha = 'http://www.google.com/accounts/' + data.get('CaptchaUrl', '')
        self.token = data.get('CaptchaToken', '')
        self.solved = None
        self.message = msg

    def __str__(self):
        return self.message


class TokenExpired(AuthenticationError):
    """ You are using an expired authentication token """


class VideoException(Exception):
    """ Failed to access a video """


class QuotaException(VideoException):
    """ Too many recent calls """


class PrivateVideoException(VideoException):
    """ Tried to access a video that is marked as private """


class NoSuchVideoException(VideoException):
    """ Tried to access a video that does not exist or has been deleted """


class VideoUpdateException(VideoException):
    """ Failed to update a video """
    def __init__(self, msg, data={}):
        self.url = data.get('url', '')
        self.request_body = data.get('request_body', '')
        self.headers = data.get('headers', '')
        self.response = data.get('response', '')
        self.response_body = data.get('response_body', '')
        self.message = msg

    def __str__(self):
        return self.message
