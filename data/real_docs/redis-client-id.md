The command just returns the ID of the current connection. Every connection
ID has certain guarantees:

1. It is never repeated, so if CLIENT ID returns the same number, the caller can be sure that the underlying client did not disconnect and reconnect the connection, but it is still the same connection.
2. The ID is monotonically incremental. If the ID of a connection is greater than the ID of another connection, it is guaranteed that the second connection was established with the server at a later time.

This command is especially useful together with CLIENT UNBLOCK which was
introduced also in Redis 5 together with CLIENT ID . Check the CLIENT UNBLOCK command page for a pattern involving the two commands.

## Examples

redis> CLIENT ID

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | Because Redis Software clustering allows multiple active proxies, CLIENT ID cannot guarantee incremental IDs between clients that connect to different nodes under multi proxy policies. |

## Return information

Integer reply: the ID of the client.

-tab-sep-

Integer reply: the ID of the client.