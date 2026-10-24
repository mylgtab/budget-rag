This command is useful in order to modify a node's view of the cluster
configuration. Specifically it assigns a set of hash slots to the node
receiving the command. If the command is successful, the node will map
the specified hash slots to itself, and will start broadcasting the new
configuration.

However note that:

1. The command only works if all the specified slots are, from the point of view of the node receiving the command, currently not assigned. A node will refuse to take ownership for slots that already belong to some other node (including itself).
2. The command fails if the same slot is specified multiple times.
3. If one of the specified slots is marked as importing , Redis clears that temporary state after the node assigns the previously unbound slot to itself. At that point, the slot belongs to the node, so it is no longer being imported.

## Required arguments

slot [slot ...]

One or more hash slots to assign to the current node.

## Examples

The following command assigns slots 1, 2, and 3 to the node receiving
the command:

 > CLUSTER ADDSLOTS 1 2 3
 OK

If you try to execute the same command again on the same node, Redis will return an error because the slots
are already assigned:

 > CLUSTER ADDSLOTS 1 2 3
 ERR Slot 1 is already busy

## Details

### Usage in Redis Cluster

This command only works in cluster mode and is useful in the following
Redis Cluster operations:

1. To create a new cluster ADDSLOTS is used in order to initially setup master nodes splitting the available hash slots among them.
2. In order to fix a broken cluster where certain slots are unassigned.

### Information about slots propagation and warnings

Note that once a node assigns a set of slots to itself, it will start
propagating this information in heartbeat packet headers. However the
other nodes will accept the information only if they have the slot as
not already bound with another node, or if the configuration epoch of the
node advertising the new hash slot, is greater than the node currently listed
in the table.

This means that this command should be used with care only by applications
orchestrating Redis Cluster, like redis-cli , and the command if used
out of the right context can leave the cluster in a wrong state or cause
data loss.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

Simple string reply: OK if the command was successful. Otherwise an error is returned.

-tab-sep-

Simple string reply: OK if the command was successful. Otherwise an error is returned.