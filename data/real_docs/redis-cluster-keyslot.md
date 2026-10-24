Returns an integer identifying the hash slot the specified key hashes to.
This command is mainly useful for debugging and testing, since it exposes
via an API the underlying Redis implementation of the hashing algorithm.
Example use cases for this command:

1. Client libraries may use Redis in order to test their own hashing algorithm, generating random keys and hashing them with both their local implementation and using Redis CLUSTER KEYSLOT command, then checking if the result is the same.
2. Humans may use this command in order to check what is the hash slot, and then the associated Redis Cluster node, responsible for a given key.

The command uses the full Redis Cluster hashing algorithm, including support for hash tags. If a key contains a valid hash tag, Redis hashes only the part of the key between { and } . You can use hash tags to force multiple keys into the same hash slot so they are handled by the same node.

## Required arguments

key

The key name to compute the hash slot for.

## Examples

[code example]

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | Only supported with the OSS cluster API. |

## Return information

Integer reply: The hash slot number for the specified key

-tab-sep-

Integer reply: The hash slot number for the specified key