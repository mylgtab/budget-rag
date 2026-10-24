> [!NOTE]
> This command's behavior varies in clustered Redis environments. See the multi-key operations page for more information.

 BRPOP is a blocking list pop primitive.
It is the blocking version of RPOP because it blocks the connection when there
are no elements to pop from any of the given lists.
An element is popped from the tail of the first list that is non-empty, with the
given keys being checked in the order that they are given.

See the BLPOP documentation for the exact semantics, since BRPOP is
identical to BLPOP with the only difference being that it pops elements from
the tail of a list instead of popping from the head.

## Required arguments

key [key ...]

One or more keys of lists to operate on.

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
* Nil reply: no element could be popped and the timeout expired.
* Array reply: the key from which the element was popped and the value of the popped element

-tab-sep-

One of the following:
* Null reply: no element could be popped and the timeout expired.
* Array reply: the key from which the element was popped and the value of the popped element