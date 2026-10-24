The CLUSTER DELSLOTSRANGE command is similar to the CLUSTER DELSLOTS command in that they both remove hash slots from the node.
The difference is that CLUSTER DELSLOTS takes a list of hash slots to remove from the node, while CLUSTER DELSLOTSRANGE takes a list of slot ranges (specified by start and end slots) to remove from the node.

## Required arguments

start-slot end-slot [start-slot end-slot ...]

One or more inclusive ranges of hash slots to unassign from the current node.

## Examples

To remove slots 1 2 3 4 5 from the node, the CLUSTER DELSLOTS command is:

 > CLUSTER DELSLOTS 1 2 3 4 5
 OK

The same operation can be completed with the following CLUSTER DELSLOTSRANGE command:

 > CLUSTER DELSLOTSRANGE 1 5
 OK

However, note that:

1. The command only works if all the specified slots are already associated with the node.
2. The command fails if the same slot is specified multiple times.
3. As a side effect of the command execution, the node may go into *down* state because not all hash slots are covered.

## Details

### Usage in Redis Cluster

This command only works in cluster mode and may be useful for
debugging and in order to manually orchestrate a cluster configuration
when a new cluster is created. It is currently not used by redis-cli ,
and mainly exists for API completeness.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

Simple string reply: OK if the command was successful. Otherwise an error is returned.

-tab-sep-

Simple string reply: OK if the command was successful. Otherwise an error is returned.