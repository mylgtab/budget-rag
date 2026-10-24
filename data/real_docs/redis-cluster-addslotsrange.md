The CLUSTER ADDSLOTSRANGE is similar to the CLUSTER ADDSLOTS command in that they both assign hash slots to nodes.

The difference between the two commands is that CLUSTER ADDSLOTS takes a list of slots to assign to the node, while CLUSTER ADDSLOTSRANGE takes a list of slot ranges (specified by start and end slots) to assign to the node.

## Required arguments

start-slot end-slot [start-slot end-slot ...]

One or more inclusive ranges of hash slots to assign to the current node.

## Examples

To assign slots 1 2 3 4 5 to the node, the CLUSTER ADDSLOTS command is:

 > CLUSTER ADDSLOTS 1 2 3 4 5
 OK

The same operation can be completed with the following CLUSTER ADDSLOTSRANGE command:

 > CLUSTER ADDSLOTSRANGE 1 5
 OK

## Details

### Usage in Redis Cluster

This command only works in cluster mode and is useful in the following Redis Cluster operations:

1. To create a new cluster, CLUSTER ADDSLOTSRANGE is used to initially set up master nodes splitting the available hash slots among them.
2. In order to fix a broken cluster where certain slots are unassigned.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

Simple string reply: OK if the command was successful. Otherwise an error is returned.

-tab-sep-

Simple string reply: OK if the command was successful. Otherwise an error is returned.