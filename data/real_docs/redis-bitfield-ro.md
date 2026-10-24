Read-only variant of the BITFIELD command.
It is like the original BITFIELD but only accepts GET subcommand and can safely be used in read-only replicas.

Since the original BITFIELD has SET and INCRBY options it is technically flagged as a writing command in the Redis command table.
For this reason read-only replicas in a Redis Cluster will redirect it to the master instance even if the connection is in read-only mode (see the READONLY command of Redis Cluster).

Since Redis 6.2, the BITFIELD_RO variant was introduced in order to allow BITFIELD behavior in read-only replicas without breaking compatibility on command flags.

See original BITFIELD for more details.

## Required arguments

key

The name of the key that holds the string.

## Optional arguments

GET encoding offset

Return the value at offset , interpreted with encoding (for example u8 or i16 ). May be given multiple times.

## Examples

[code example]

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | |

## Return information

Array reply: each entry being the corresponding result of the sub-command given at the same position.

-tab-sep-

Array reply: each entry being the corresponding result of the sub-command given at the same position.