Use this command from one connection to unblock a client that is blocked by a blocking operation, such as BRPOP , XREAD , or WAIT .

By default, Redis unblocks the client as if the blocked command timed out. You can pass an optional argument to choose the unblocking behavior: TIMEOUT, the default, or ERROR. If you specify ERROR, Redis unblocks the client and returns an error that indicates the client was force-unblocked.Specifically the client will receive the following error:

 -UNBLOCKED client unblocked via CLIENT UNBLOCK

The error text may change over time, but the error code will remain -UNBLOCKED .

## Required arguments

client-id

The ID of the client to unblock.

## Optional arguments

TIMEOUT | ERROR

How to unblock the client: as if its timeout expired ( TIMEOUT , the default), or by returning an error ( ERROR ).

## Details

Use this command when you need to monitor many keys with a limited number of connections. For example, you might monitor multiple streams with XREAD without using more than N connections. If your consumer process needs to monitor another stream key, you can avoid opening another connection: unblock one of the connections in the pool, add the new key, and issue the blocking command again.

To use this pattern, create an additional control connection that sends CLIENT UNBLOCK when needed. Before you run a blocking operation on each monitored connection, run CLIENT ID to get that connection’s ID. When you need to add or remove a key, use the control connection to send CLIENT UNBLOCK for the connection that is running the blocking command. The blocking command returns, and you can then reissue it with the updated set of keys.

The following example uses Redis Streams, but you can apply the same pattern to other blocking operations.

[code example]

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | |

## Return information

One of the following:
* Integer reply: 1 if the client was unblocked successfully.
* Integer reply: 0 if the client wasn't unblocked.

-tab-sep-

One of the following:
* Integer reply: 1 if the client was unblocked successfully.
* Integer reply: 0 if the client wasn't unblocked.