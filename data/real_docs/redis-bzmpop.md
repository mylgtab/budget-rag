> [!NOTE]
> This command's behavior varies in clustered Redis environments. See the multi-key operations page for more information.

 BZMPOP is the blocking variant of ZMPOP .

When any of the sorted sets contains elements, this command behaves exactly like ZMPOP .
When used inside a MULTI / EXEC block or a Lua script, this command behaves exactly like ZMPOP .
When all sorted sets are empty, Redis will block the connection until another client adds members to one of the keys or until the timeout (a double value specifying the maximum number of seconds to block) elapses.
A timeout of zero can be used to block indefinitely.

See ZMPOP for more information.

## Required arguments

timeout

The maximum time to block, in seconds. A timeout of 0 blocks indefinitely.

numkeys

The number of keys that follow.

key [key ...]

One or more sorted-set keys to pop from.

MIN | MAX

Pop the members with the lowest scores ( MIN ) or the highest scores ( MAX ).

## Optional arguments

COUNT count

The number of members to pop. Defaults to 1.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | |

## Return information

One of the following:
* Nil reply: when no element could be popped.
* Array reply: a two-element array with the first element being the name of the key from which elements were popped, and the second element is an array of the popped elements. Every entry in the elements array is also an array that contains the member and its score.

-tab-sep-

One of the following:
* Null reply: when no element could be popped.
* Array reply: a two-element array with the first element being the name of the key from which elements were popped, and the second element is an array of the popped elements. Every entry in the elements array is also an array that contains the member and its score.