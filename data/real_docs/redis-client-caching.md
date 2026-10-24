This command controls the tracking of the keys in the next command executed
by the connection, when tracking is enabled in OPTIN or OPTOUT mode.
Please check the
client side caching documentation for
background information.

When tracking is enabled in Redis, using the CLIENT TRACKING command, it is
possible to specify the OPTIN or OPTOUT options, so that keys
in read only commands are not automatically remembered by the server to
be invalidated later. When we are in OPTIN mode, we can enable the
tracking of the keys in the next command by calling CLIENT CACHING YES 
immediately before it. Similarly when we are in OPTOUT mode, and keys
are normally tracked, we can avoid the keys in the next command to be
tracked using CLIENT CACHING NO .

Basically the command sets a state in the connection, that is valid only
for the next command execution, that will modify the behavior of client
tracking.

## Required arguments

YES | NO

Whether to cache keys for the next command ( YES ) or not ( NO ) when tracking is in OPTIN / OPTOUT mode.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | |

## Return information

Simple string reply: OK or an error if the argument is not "yes" or "no".

-tab-sep-

Simple string reply: OK or an error if the argument is not "yes" or "no".