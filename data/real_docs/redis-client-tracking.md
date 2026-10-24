This command enables the tracking feature of the Redis server, which is used
for server assisted client side caching.

When tracking is enabled Redis remembers the keys that the connection
requested, in order to send later invalidation messages when such keys are
modified. Invalidation messages are sent in the same connection (only available
when the RESP3 protocol is used) or redirected in a different connection
(available with RESP2 and Pub/Sub). You can use broadcasting mode to receive notifications for all keys that match the key prefixes you subscribe to, regardless of which keys you request. For details, see the client-side caching documentation. This page only describes the options for this subcommand.

In order to enable tracking, use:

 CLIENT TRACKING ON ... options ...

The feature will remain active in the current connection for all its life,
unless tracking is turned off with CLIENT TRACKING OFF at some point.

## Required arguments

ON | OFF

Turn key-invalidation tracking on or off for the connection.

## Optional arguments

REDIRECT client-id

Send invalidation messages to the connection with the specified ID. The connection must exist. You can get the ID of a connection using CLIENT ID . If the redirected connection terminates while in RESP3 mode, the connection with tracking enabled receives tracking-redir-broken push messages to signal the disconnection.

PREFIX prefix [PREFIX prefix ...]

Track only keys that start with one of the specified prefixes. Use with the BCAST argument. You can specify this option multiple times to track multiple prefixes. If you enable broadcasting without this option, Redis sends invalidation messages for every key. You can’t remove a single prefix; to remove all prefixes, disable and re-enable tracking. This option adds O(N^2) time complexity, where N is the total number of tracked prefixes.

BCAST

Enable broadcasting mode. In this mode, Redis sends invalidation messages for all keys, or for keys that match a specified PREFIX, instead of only the keys that the connection reads. Without broadcasting mode, Redis tracks the keys fetched by read-only commands and sends invalidation messages only for those keys.

OPTIN

Track keys only for read commands that immediately follow a CLIENT CACHING YES .

OPTOUT

Track all read keys except those for commands that immediately follow a CLIENT CACHING NO .

NOLOOP

Do not send invalidation messages for keys modified by this connection. In the default tracking mode, modifying a tracked key removes it from the invalidation table, even when NOLOOP suppresses the message. To track the key for future invalidations, read the key again.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | |

## Return information

Simple string reply: OK if the connection was successfully put in tracking mode or if the tracking mode was successfully disabled. Otherwise, an error is returned.

-tab-sep-

Simple string reply: OK if the connection was successfully put in tracking mode or if the tracking mode was successfully disabled. Otherwise, an error is returned.