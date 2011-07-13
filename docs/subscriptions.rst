=============
Subscriptions
=============

Get the channels a user is subscribed to
----------------------------------------
Client.user_subscriptions(`username`)
    Authenticated clients may omit the `username` parameter to fetch a stream
    of usernames that the authenticated user is subscribed to.::

        c = pytube.Client('app_id')
        c.user_subscriptions('TheOfficialSkrillex)


Subscribe the Authenticated User to a channel
---------------------------------------------
Client.subscribe(`username`)
    Authenticated clients may call this method to subscribe to a channel.

PyTube doesn't have an unsubscribe method yet. =(
