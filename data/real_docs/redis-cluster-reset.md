Use CLUSTER RESET to reset a Redis Cluster node. Specify SOFT or HARD to choose the reset type.

Before you reset a primary node, remove all keys from it, for example with FLUSHALL. Redis does not reset primary nodes that contain keys.

Effects on the node:

1. All the other nodes in the cluster are forgotten.
2. All the assigned / open slots are reset, so the slots-to-nodes mapping is totally cleared.
3. If the node is a replica its dataset is flushed, transforming the node to an empty master.
4. HARD reset only: a new Node ID is generated.
5. HARD reset only: currentEpoch and configEpoch variables are set to 0.
6. The new configuration is persisted on disk in the node cluster configuration file.

This command is mainly useful to reprovision a Redis Cluster node
in order to be used in the context of a new, different cluster. The command
is also extensively used by the Redis Cluster testing framework in order to
reset the state of the cluster every time a new test unit is executed.

If no reset type is specified, the default is soft .

## Optional arguments

HARD | SOFT

 SOFT (the default) resets the node but keeps its node ID; HARD also assigns a new node ID and clears additional state.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

Simple string reply: OK if the command was successful. Otherwise an error is returned.

-tab-sep-

Simple string reply: OK if the command was successful. Otherwise an error is returned.