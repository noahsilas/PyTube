=================
The Pytube Client
=================

Instantiating
=============
When creating a Client, you must supply an application identifier. This is
an arbitrary string you can choose to identify the application submitting
API requests.

You may also specify a `developer key`_. This is recommended for high volume
applications.

.. _developer key: http://code.google.com/apis/youtube/dashboard/

Authenticating
==============
Authenticating the client enables a number of actions to be taken on behalf
of a user and may cause some API results for content that the authenticated
user to include additional or private data.

You can authenticate a client against a youtube account through google's 
ClientLogin or AuthSub::

    c = pytube.Client('appid')
    # Client Login
    c.authenticate(channelname, password)

    # Authsub Login
    c.authenticate(authsub=token)


Captcha Requests When Authenticating
------------------------------------
Sometimes google will request that you complete a captcha when authenticating
via ClientLogin. Here is an example of how to handle this in a console-based app::

    while True:
        captcha = None
        try:
            c.authenticate(channelname, password, captcha)
            break
        except pytube.CaptchaRequired, captcha:
            print "please solve the captcha at %s" % captcha.captcha
            captcha.solved = raw_input('>>> ')


pytube.CaptchaRequired has the following attributes:
    * `token` - a unique token that must be submitted with the solved captcha
    * `captcha` - the url of a captcha image to be solved

If you don't want to store the exception, you may create an object to pass
into authenticate from a token and a solved captcha. Anything supplying the
attributes `token` and `solved` will work::

    class SolvedCaptcha(object):
        def __init__(self, token, solved):
            self.token = token
            self.solved = solved

