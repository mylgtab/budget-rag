> [!NOTE]
> This command's behavior varies in clustered Redis environments. See the multi-key operations page for more information.

 BRPOPLPUSH is the blocking variant of RPOPLPUSH .
When source contains elements, this command behaves exactly like RPOPLPUSH .
When used inside a MULTI / EXEC block or a Lua script, this command behaves exactly like RPOPLPUSH .
When source is empty, Redis will block the connection until another client
pushes to it or until timeout is reached.
A timeout of zero can be used to block indefinitely.

See RPOPLPUSH for more information.

## Required arguments

source

The key of the source list.

destination

The key of the destination list.

timeout

The maximum time to block, in seconds. A timeout of 0 blocks indefinitely.

## Details

### Pattern: reliable queue

Please see the pattern description in the RPOPLPUSH documentation.

### Pattern: circular list

Please see the pattern description in the RPOPLPUSH documentation.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | Deprecated as of Redis v6.2.0. |

## Return information

One of the following:
* Bulk string reply: the element being popped from _source_ and pushed to _destination_.
* Nil reply: the timeout is reached.

-tab-sep-

One of the following:
* Bulk string reply: the element being popped from _source_ and pushed to _destination_.
* Null reply: the timeout is reached.