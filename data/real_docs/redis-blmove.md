> [!NOTE]
> This command's behavior varies in clustered Redis environments. See the multi-key operations page for more information.

 BLMOVE is the blocking variant of LMOVE .
When source contains elements, this command behaves exactly like LMOVE .
When used inside a MULTI / EXEC block or a Lua script, this command behaves exactly like LMOVE .
When source is empty, Redis will block the connection until another client
pushes to it or until timeout (a double value specifying the maximum number of seconds to block) is reached.
A timeout of zero can be used to block indefinitely.

This command comes in place of the now deprecated BRPOPLPUSH . Doing
 BLMOVE RIGHT LEFT is equivalent.

See LMOVE for more information.

## Required arguments

source

The key of the source list.

destination

The key of the destination list.

LEFT | RIGHT

The end of source to pop the element from: LEFT (head) or RIGHT (tail).

LEFT | RIGHT

The end of destination to push the element to: LEFT (head) or RIGHT (tail).

timeout

The maximum time to block, in seconds. A timeout of 0 blocks indefinitely.

## Details

### Pattern: reliable queue

Please see the pattern description in the LMOVE documentation.

### Pattern: circular list

Please see the pattern description in the LMOVE documentation.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | |

## Return information

One of the following:
* Bulk string reply: the element being popped from the _source_ and pushed to the _destination_.
* Nil reply: the operation timed-out

-tab-sep-

One of the following:
* Bulk string reply: the element being popped from the _source_ and pushed to the _destination_.
* Null reply: the operation timed-out