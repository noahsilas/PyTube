class YtData(object):
    """Provides some base functions for parsing common youtube responses"""

    feed_types = {
        'favorites': u'http://gdata.youtube.com/schemas/2007#user.favorites',
        'contacts': u'http://gdata.youtube.com/schemas/2007#user.contacts',
        'inbox': u'http://gdata.youtube.com/schemas/2007#user.inbox',
        'playlists': u'http://gdata.youtube.com/schemas/2007#user.playlists',
        'subscriptions': u'http://gdata.youtube.com/schemas/2007#user.subscriptions',
        'uploads': u'http://gdata.youtube.com/schemas/2007#user.uploads',
        'newsubscriptionvideos': u'http://gdata.youtube.com/schemas/2007#user.newsubscriptionvideos',
    }
    reverse_feed_types = dict([(v,k) for k,v in feed_types.iteritems()])

    def _parse_feeds(self, feeds):
        self.feeds = {}
        for feed in feeds:
            try:
                feedtype = self.reverse_feed_types[feed[u'rel']]
            except KeyError:
                print 'unknown feed relation: %s' % feed[u'rel']
                logging.debug('unknown feed relation: %s' % feed[u'rel'])
                continue
            self.feeds[feedtype] = feed[u'href']
            if u'countHint' in feed:
                setattr(self, feedtype + '_count', feed[u'countHint'])


class Stream(YtData):
    """ Implements get and slice operations against the notion of a youtube
        result stream. This allows us to expose paginated results from the
        youtube API via the normal python index/slice notation.

        Maintains an internal results cache in order to minimize youtube API
        hits.
    """

    # constants enforced by the API
    MAX_PAGE_SIZE = 50
    MAX_RESULTS = 1000

    def __init__(self, client, uri, query=None):
        self.client = client
        self.uri = uri
        self.query = query or {}

        self._result_cache = []
        self._count = None

    def __len__(self):
        return self.count

    def __iter__(self):
        i = 0
        exhausted = False
        while 1:
            while i < len(self._result_cache):
                yield self._result_cache[i]
                i += 1
            if ((self._count is not None and i >= self._count) or
                len(self._result_cache) == self.MAX_RESULTS or
                exhausted):
                raise StopIteration
            if self._fill_cache(self.MAX_PAGE_SIZE) < self.MAX_PAGE_SIZE:
                exhausted = True

    def __getitem__(self, key):
        if not isinstance(key, (int, long, slice)):
            raise TypeError
        if ((not isinstance(key, slice) and (key < 0))
            or (isinstance(key, slice) and ((key.start or 0) < 0)
                and ((key.stop or 0) < 0))):
            raise ValueError("Negative indexing is not supported")

        if isinstance(key, (int, long)):
            if key >= self.MAX_RESULTS:
                raise IndexError(
                    "Youtube API only supports fetching %s entries from a "
                    "Video Stream" % self.MAX_RESULTS)
            if self._count is not None and self._count < key:
                raise IndexError
            if key < len(self._result_cache):
                return self._result_cache[key]
            # Can we get the key as part of a query that will fill the next
            # chunk of our result cache?
            if key <= len(self._result_cache) + self.MAX_PAGE_SIZE:
                self._fill_cache(self.MAX_PAGE_SIZE)
                return self._result_cache[key]
            return self.get_at_index(key)

        if key.stop <= len(self._result_cache):
            return self._result_cache[key]
        if key.start <= len(self._result_cache) + self.MAX_PAGE_SIZE:
            self._fill_cache(key.stop - len(self._result_cache))
            return self._result_cache[key]
        return self.get_slice(key)

    @property
    def count(self):
        """ Returns the total number of objects in this stream.

            Most YouTube streams are limited to 1000 results, but this
            limitation is not reflected by Stream.count, which will instead
            return the total number of objects in the stream, some of which
            may not be accessible via API.
         """
        if self._count is not None:
            return self._count
        self._fill_cache(self.MAX_PAGE_SIZE)
        return self._count

    def get_at_index(self, index):
        query = self.query.copy()
        query.update({'max-results': 1, 'start-index': index, 'v': 2})
        data = self.client._gdata_json(self.uri, query)
        if u'entry' in data[u'feed']:
            return self._handle_data(data)[0]
        raise IndexError

    def get_slice(self, key):
        # youtube results are 1-indexed, while python slices are 0-indexed.
        # offset start and stop by 1
        start, stop =  key.start + 1, key.stop + 1
        index = start
        results = []
        while index < stop:
            query = self.query.copy()
            query.update({
                'max-results': min(stop - index, 50),
                'start-index': index,
                'v': 2
            })
            data = self._handle_data(self.client._gdata_json(self.uri, query))
            index += len(data)
            results += data
            if len(data) < query['max-results']: break
        return results

    def _fill_cache(self, count):
        start = len(self._result_cache)
        stop = start + count
        data = self.get_slice(slice(start, stop))
        self._result_cache += data
        return len(data)

    def _handle_data(self, data):
        """ Left to subclasses to implement.

            Well behaved stream classes should update self._count when
            overriding this method.
        """
        raise NotImplemented
