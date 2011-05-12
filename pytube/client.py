try: import simplejson as json
except ImportError: import json
import urllib, urllib2
import datetime
import warnings
import logging

from pytube.stream import Stream, YtData
from pytube.utils import yt_ts_to_datetime
import pytube.exceptions


class LinksMixin(object):
    """ Provides parsing of strangely formatted youtube api links objects
    """
    def _parse_links(self, links):
        self._links = {}
        for link in links:
            body = link.copy()
            del body[u'rel']
            name = link[u'rel']
            if name.startswith('http://gdata.youtube.com/schemas/2007#'):
                name = name[len('http://gdata.youtube.com/schemas/2007#'):]
            self._links[name] = body

        # check to see if we can set up some useful references
        if 'video.related' in self._links:
            self.related_videos = VideoStream(self.client, self._links['video.related'][u'href'])
        if 'video.responses' in self._links:
            self.video_responses = VideoStream(self.client, self._links['video.responses'][u'href'])
        if 'insight.views' in self._links:
            self.insight_url = self._links['insight.views']['href']


class Profile(YtData, LinksMixin):
    """ Collects data about a YouTube user/channel. """

    def __init__(self, client, data):
        assert data[u'version'] == u'1.0', "Youtube API version mismatch"
        self.client = client
        entry = data[u'entry']

        self.id = entry[u'yt$username'][u'$t']
        self.api_id = entry[u'id'][u'$t']
        self.thumbnail = entry[u'media$thumbnail'][u'url']
        self.title = entry[u'title'][u'$t']
        self.updated = yt_ts_to_datetime(entry[u'updated'][u'$t'])
        self.author = {
            'name': entry[u'author'][0][u'name'][u'$t'],
            'username': entry[u'yt$username'][u'$t'],
            'age': entry[u'yt$age'][u'$t'],
            'location': entry[u'yt$location'][u'$t'],
        }
        if u'yt$gender' in entry:
            self.author['gender'] = entry[u'yt$gender'][u'$t']

        self.statistics = entry[u'yt$statistics'].copy()
        self.statistics[u'lastWebAccess'] = yt_ts_to_datetime(self.statistics[u'lastWebAccess'])
        self.statistics[u'subscriberCount'] = int(self.statistics[u'subscriberCount'])
        self.statistics[u'totalUploadViews'] = int(self.statistics[u'totalUploadViews'])
        self.statistics[u'videoWatchCount'] = int(self.statistics[u'videoWatchCount'])
        self.statistics[u'viewCount'] = int(self.statistics[u'viewCount'])

        self._parse_feeds(entry['gd$feedLink'])
        self._parse_links(entry['link'])

    def subscribe(self):
        self.client.subscribe(self.author['username'])

    def subscriptions(self):
        return self.client.user_subscriptions(self.author['username'])

    def __repr__(self):
        return "<YouTube Profile: %s>" % (str(self.id),)

    def __unicode__(self):
        return u"<YouTube Profile: %s>" % (str(self.id),)


class Video(YtData, LinksMixin):
    """ Collects data about a YouTube Video. """

    def _parse_categories(self, data):
        self.categories = [(c[u'term'], c[u'label']) for c in data if c['scheme'] == u'http://gdata.youtube.com/schemas/2007/categories.cat']
        self.keywords = [c['term'] for c in data if c['scheme'] == u'http://gdata.youtube.com/schemas/2007/keywords.cat']
        return

    def __init__(self, client, data):
        self.client = client
        self._parse_links(data[u'link'])
        self._parse_categories(data[u'category'])

        self.title = data[u'title'][u'$t']
        self.author = data[u'author'][0][u'name'][u'$t']
        self.api_id = data[u'id']['$t']
        try:
            self.id = data[u'media$group'][u'yt$videoid'][u'$t']
        except KeyError:
            assert data[u'id'][u'$t'].startswith('http://gdata.youtube.com/feeds/api/videos/')
            assert len(data[u'id'][u'$t']) == 53
            self.id = data[u'id'][u'$t'][-11:]

        self.published = yt_ts_to_datetime(data[u'published'][u'$t'])
        self.updated = yt_ts_to_datetime(data[u'updated'][u'$t'])

        if u'yt$rating' in data:
            self.like_count = int(data[u'yt$rating'][u'numLikes'])
            self.dislike_count = int(data[u'yt$rating'][u'numDislikes'])

        self.comments = self.client.video_comments(self.id)

        # All the following attributes don't exist for certain restricted videos
        if u'media$description' in u'media$group':
            self.description = data[u'media$group'][u'media$description']
        if u'yt$uploaded' in data[u'media$group']:
            self.uploaded = yt_ts_to_datetime(data[u'media$group'][u'yt$uploaded'][u'$t'])
        if u'yt$duration' in data[u'media$group']:
            self.duration = int(data[u'media$group'][u'yt$duration'][u'seconds'])
        if u'yt$aspectRatio' in data[u'media$group']:
            self.aspect_ratio = data[u'media$group'][u'yt$aspectRatio'][u'$t']
        if u'yt$statistics' in data:
            self.favorite_count = int(data[u'yt$statistics'][u'favoriteCount'])
            self.view_count = int(data[u'yt$statistics'][u'viewCount'])
        if u'gd$comments' in data:
            self.comment_count = int(data[u'gd$comments'][u'gd$feedLink'][u'countHint'])
            self.comments._count = self.comment_count

    def __repr__(self):
        return "<YouTube Video: %s>" % (str(self.id),)

    def __unicode__(self):
        return u"<YouTube Video: %s>" % (str(self.id),)


class VideoStream(Stream, LinksMixin):
    """ Stream for parsing YouTube Video results """

    def _handle_data(self, data):
        assert data[u'version'] == u'1.0', "Youtube API version mismatch"
        self._count = int(data[u'feed'][u'openSearch$totalResults'][u'$t'])
        self.title = data[u'feed'][u'title'][u'$t']
        self.updated = yt_ts_to_datetime(data[u'feed'][u'updated'][u'$t'])
        self._parse_links(data[u'feed'][u'link'])
        return [Video(self.client, x) for x in data['feed']['entry']]

    def __repr__(self):
        return "<YouTube VideoStream: %s>" % (self.uri,)

    def __unicode__(self):
        return u"<YouTube VideoStream: %s>" % (self.uri,)


class SubscriptionStream(Stream):
    """ Stream for parsing YouTube Subscription results """

    def _handle_data(self, data):
        assert data[u'version'] == u'1.0', "Youtube API version mismatch"
        self._count = int(data[u'feed'][u'openSearch$totalResults'][u'$t'])
        subscriptions = data['feed'].get('entry', ())
        return [subscription['yt$username']['$t'] for subscription in subscriptions]

    def __repr__(self):
        return "<YouTube Subscriptions: %s>" % (self.uri,)

    def __unicode__(self):
        return u"<YouTube VideoStream: %s>" % (self.uri,)


class Comment(object):
    """ Transforms YouTube API response into a usable comment object with
        native datatypes.
    """
    def __init__(self, data):
        self.id = data[u'id'][u'$t']
        self.author = data[u'author'][0][u'name'][u'$t']
        self.title = data[u'title'][u'$t']
        self.content = data[u'content'][u'$t']
        self.published = yt_ts_to_datetime(data[u'published'][u'$t'])
        self.updated = yt_ts_to_datetime(data[u'updated'][u'$t'])


class CommentStream(Stream, LinksMixin):
    """ Stream for parsing YouTube Comment results """
    def _handle_data(self, data):
        assert data[u'version'] == u'1.0', "Youtube API version mismatch"
        self._count = int(data[u'feed'][u'openSearch$totalResults'][u'$t'])
        self.title = data[u'feed'][u'title'][u'$t']
        self.updated = yt_ts_to_datetime(data[u'feed'][u'updated'][u'$t'])
        self._parse_links(data[u'feed'][u'link'])
        return [Comment(d) for d in data['feed']['entry']]


class Client(object):
    """ The YouTube API Client

        You must provide an app identifier to use the youtube API.
        You may also provide a developer API key (http://code.google.com/apis/youtube/dashboard/)
        which will be submitted with all API requests.
    """

    GOOGLE_AUTH_URL = 'https://www.google.com/accounts/ClientLogin'
    YOUTUBE_SEARCH_URL = 'http://gdata.youtube.com/feeds/api/videos'
    YOUTUBE_VIDEO_URL = 'http://gdata.youtube.com/feeds/api/videos/%(video_id)s'
    YOUTUBE_PROFILE_URL = 'http://gdata.youtube.com/feeds/api/users/%(username)s'
    YOUTUBE_UPLOADS_URL = 'http://gdata.youtube.com/feeds/api/users/%(username)s/uploads'
    YOUTUBE_COMMENTS_URL = 'http://gdata.youtube.com/feeds/api/videos/%(video_id)s/comments'
    YOUTUBE_SUBSCRIBE_URL = 'http://gdata.youtube.com/feeds/api/users/default/subscriptions'
    YOUTUBE_SUBSCRIPTIONS_URL = 'http://gdata.youtube.com/feeds/api/users/%(username)s/subscriptions?alt=json&v=2'

    def __init__(self, app_name, dev_key=None):
        self._auth_data = None
        self.username = None
        self.app_name = app_name
        self.dev_key = dev_key

    def _gdata_request(self, url, query=None, data=None, headers=None, timeout=None):
        if query:
            sep = '?' if '?' not in url else '&'
            url += sep + urllib.urlencode(query)

        headers = headers or {}
        headers.update(self._auth_headers())
        if self.dev_key:
            headers['X-GData-Key'] = 'key=' + self.dev_key

        request = urllib2.Request(url, data, headers)
        return urllib2.urlopen(request, timeout=timeout)

    def _gdata_json(self, url, query=None, data=None, headers=None):
        query = query or {}
        query.update({'alt': 'json'})
        return json.load(self._gdata_request(url, query, data, headers))

    def _auth_headers(self):
        if self._auth_data is None:
            return {}
        if 'Auth' in self._auth_data:
            return {
                'Authorization': "GoogleLogin auth=" + self._auth_data['Auth'],
            }
        if 'authsub_token' in self._auth_data:
            return {
                'Authorization': "AuthSub token=" + self._auth_data['authsub_token'],
            }
        return {}

    def _client_login(self, username, password, captcha=None):
        """ Try to login with gdata ClientLogin"""
        auth_data = {
            'Email': username,
            'Passwd': password,
            'service': 'youtube',
            'source': self.app_name,
        }
        if captcha:
            auth_data.update({
                'logintoken': captcha.token,
                'logincaptcha': captcha.solved,
            })
        auth_data = urllib.urlencode(auth_data)
        try:
            response = self._gdata_request(
                self.GOOGLE_AUTH_URL,
                query=None,
                data=auth_data
            )
        except urllib2.HTTPError, e:
            # convert the response into a usable error dict
            response = e.read()
            data = dict([r.split('=', 1) for r in response.strip().split()])
            # we just trashed the response iterator; put the response back in
            # an attribute on the exception that the caller can read.
            e.response = response

            if e.getcode() == 403:
                errors = {
                    'BadAuthentication': "Invalid Credentials",
                    "AccountDisabled": "Account Disabled",
                }
                reason = errors.get(data.get('Error', None), None)
                if reason is not None:
                    raise pytube.exceptions.AuthenticationError(reason)
                if data.get('Error', None) == 'CaptchaRequired':
                    raise pytube.exceptions.CaptchaRequired(data)
            raise

        self._auth_data = dict([r.split('=') for r in response.read().split()])
        self.username = username

    def _authsub_login(self, token):
        """Authenticates this user with an authsub token"""
        self._auth_data = {
            'authsub_token': token,
        }

    def authenticate(self, username=None, password=None, captcha=None, authsub=None):
        """ Authenticates this client with YouTube.

            You may provide either a username and password, which will invoke
            the gdata ClientLogin, or you may pass an authsub token.
        """
        assert (username and password) or authsub
        if username and password:
            self._client_login(username, password, captcha)
        elif authsub:
            self._authsub_login()

    def unauthenticate(self):
        """ Unauthenticates this client.

            This does not invalidate any login token that was generated; there
            does not seem to be an API to do that. We simply delete local
            references to the token.
        """
        self._auth_data = None
        self.username = None

    def user_profile(self, username='default'):
        """ Gets username's youtube profile. If authenticated, may be called without
            passing a username to get your own profile.
        """
        data = self._gdata_json(self.YOUTUBE_PROFILE_URL % {'username': username })
        return Profile(self, data)

    def user_videos(self, username='default'):
        """ Gets a user's uploaded video stream. If authenticated, may be
            called without passing a username to get your own videos.
        """
        return VideoStream(self, self.YOUTUBE_UPLOADS_URL % {'username': username })

    def user_subscriptions(self, username='default'):
        """ Gets YouTube channel ids that username is following. If
            authenticated, may be called without passing a username to get
            your own subscriptions.
        """
        return SubscriptionStream(self, self.YOUTUBE_SUBSCRIPTIONS_URL % {'username': username })

    def video(self, video_id):
        """ Gets a specific video from the youtube API.
        """
        try:
            data = self._gdata_json(self.YOUTUBE_VIDEO_URL % {'video_id': video_id}, {'v': 2})
        except urllib2.HTTPError, e:
            if e.code == 403:
                raise pytube.exceptions.PrivateVideoException
            if e.code == 404:
                raise pytube.exceptions.NoSuchVideoException
            raise
        return Video(self, data[u'entry'])

    def video_search(self, term):
        """ Searches YouTube for videos matching a search term
        """
        return VideoStream(self, self.YOUTUBE_SEARCH_URL, query={'q': term})

    def video_comments(self, video_id):
        """ Gets Comments for a specific video
        """
        return CommentStream(self, self.YOUTUBE_COMMENTS_URL % {'video_id': video_id})

    def subscribe(self, username='default'):
        """Subscribes the authenticated user to username's channels
        """
        assert self._auth_data is not None, "You must be authenticated to subscribe"
        subscribe_data = \
        '''<?xml version="1.0" encoding="UTF-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom"
          xmlns:yt="http://gdata.youtube.com/schemas/2007">
            <category scheme="http://gdata.youtube.com/schemas/2007/subscriptiontypes.cat"
              term="channel"/>
            <yt:username>{0}</yt:username>
        </entry>'''.format(username)
        subscribe_headers = { 'Content-Type': 'application/atom+xml'}
        response = self._gdata_request(self.YOUTUBE_SUBSCRIBE_URL, None, subscribe_data, subscribe_headers)
