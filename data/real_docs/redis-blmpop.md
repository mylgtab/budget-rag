> [!NOTE]
> This command's behavior varies in clustered Redis environments. See the multi-key operations page for more information.

 BLMPOP is the blocking variant of LMPOP .

When any of the lists contains elements, this command behaves exactly like LMPOP .
When used inside a MULTI / EXEC block or a Lua script, this command behaves exactly like LMPOP .
When all lists are empty, Redis will block the connection until another client pushes to it or until the timeout (a double value specifying the maximum number of seconds to block) elapses.
A timeout of zero can be used to block indefinitely.

See LMPOP for more information.

## Required arguments

timeout

The maximum time to block, in seconds. A timeout of 0 blocks indefinitely.

numkeys

The number of keys that follow.

key [key ...]

One or more keys of lists to operate on.

LEFT | RIGHT

The end of the list to pop elements from: LEFT (head) or RIGHT (tail).

## Optional arguments

COUNT count

The number of elements to pop. Defaults to 1.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | |

## Return information

One of the following:
* Nil reply: when no element could be popped and the _timeout_ is reached.
* Array reply: a two-element array with the first element being the name of the key from which elements were popped, and the second element being an array of the popped elements.

-tab-sep-

One of the following:
* Null reply: when no element could be popped and the _timeout_ is reached.
* Array reply: a two-element array with the first element being the name of the key from which elements were popped, and the second element being an array of the popped elements.