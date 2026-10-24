> [!NOTE]
> This command's behavior varies in clustered Redis environments. See the multi-key operations page for more information.

 BZPOPMAX is the blocking variant of the sorted set ZPOPMAX primitive.

It is the blocking version because it blocks the connection when there are no
members to pop from any of the given sorted sets.
A member with the highest score is popped from first sorted set that is
non-empty, with the given keys being checked in the order that they are given.

The timeout argument is interpreted as a double value specifying the maximum
number of seconds to block. A timeout of zero can be used to block indefinitely.

See the BZPOPMIN documentation for the exact semantics, since BZPOPMAX 
is identical to BZPOPMIN with the only difference being that it pops members
with the highest scores instead of popping the ones with the lowest scores.

## Required arguments

key [key ...]

One or more sorted-set keys to pop from.

timeout

The maximum time to block, in seconds. A timeout of 0 blocks indefinitely.

## Examples

[code example]

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | |

## Return information

One of the following:
* Nil reply: when no element could be popped and the _timeout_ expired.
* Array reply: the keyname, popped member, and its score.

-tab-sep-

One of the following:
* Null reply: when no element could be popped and the _timeout_ expired.
* Array reply: the keyname, popped member, and its score.