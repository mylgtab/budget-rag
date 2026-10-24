The command returns all the rules defined for an existing ACL user.

Specifically, it lists the user's ACL flags, password hashes, commands, key patterns, channel patterns (Added in version 6.2) and selectors (Added in version 7.0).
Additional information may be returned in the future if more metadata is added to the user.

Command rules are always returned in the same format as the one used in the ACL SETUSER command.
Before version 7.0, keys and channels were returned as an array of patterns, however in version 7.0 later they are now also returned in same format as the one used in the ACL SETUSER command.
Note: This description of command rules reflects the user's effective permissions, so while it may not be identical to the set of rules used to configure the user, it is still functionally identical.

Selectors are listed in the order they were applied to the user, and include information about commands, key patterns, and channel patterns.

## Required arguments

username

The user whose rules to return.

## Examples

Here's an example configuration for a user

[code example]

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | Not supported for scripts. |

## Return information

One of the following:
* Array reply: a list of ACL rule definitions for the user.
* Nil reply: if user does not exist.

-tab-sep-

One of the following:
* Map reply: a set of ACL rule definitions for the user
* Null reply: if user does not exist.