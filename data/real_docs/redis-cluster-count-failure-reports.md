This command returns the number of active failure reports for the specified node. Redis Cluster uses failure reports to promote a node from PFAIL to FAIL. PFAIL means the node is not reachable from one node’s point of view. FAIL means that a majority of primary nodes agreed, within a time window, that the node is not reachable.

The command counts only failure reports that have not expired. A report expires after twice the node timeout. The count includes only reports that the node receiving the command has received from other nodes. It does not include the receiving node’s own view of the specified node.

Use this command to debug Redis Cluster failure detection when it does not behave as expected.

## Required arguments

node-id

The ID of the node to count failure reports for.

## Details

* A node flags another node with PFAIL when the node is not reachable for a time greater than the configured node timeout, which is a fundamental configuration parameter of a Redis Cluster.
* Nodes in PFAIL state are provided in gossip sections of heartbeat packets.
* Every time a node processes gossip packets from other nodes, it creates (and refreshes the TTL if needed)*failure reports, remembering that a given node said another given node is in PFAIL condition.
* Each failure report has a time to live of two times the node timeout time.
* If at a given time a node has another node flagged with PFAIL , and at the same time collected the majority of other master nodes failure reports about this node (including itself if it is a master), then it elevates the failure state of the node from PFAIL to FAIL , and broadcasts a message forcing all the nodes that can be reached to flag the node as FAIL .

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

Integer reply: the number of active failure reports for the node.

-tab-sep-

Integer reply: the number of active failure reports for the node.