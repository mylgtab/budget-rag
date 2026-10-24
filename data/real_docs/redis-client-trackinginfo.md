The command returns information about the current client connection's use of the server assisted client side caching feature.

Here's the list of tracking information sections and their respective values:

* flags : A list of tracking flags used by the connection. The flags and their meanings are as follows:
 * off : The connection isn't using server assisted client side caching.
 * on : Server assisted client side caching is enabled for the connection.
 * bcast : The client uses broadcasting mode.
 * optin : The client does not cache keys by default.
 * optout : The client caches keys by default.
 * caching-yes : The next command will cache keys (exists only together with optin ).
 * caching-no : The next command won't cache keys (exists only together with optout ).
 * noloop : The client isn't notified about keys modified by itself.
 * broken_redirect : The client ID used for redirection isn't valid anymore.
* redirect : The client ID used for notifications redirection, 0 for self-redirection, or -1 when none.
* prefixes : A list of key prefixes for which notifications are sent to the client.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | |

## Return information

Array reply: a list of tracking information sections and their respective values.

-tab-sep-

Map reply: a list of tracking information sections and their respective values.