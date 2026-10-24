Each node in a Redis Cluster maintains a pair of long-lived TCP link with each peer in the cluster: One for sending outbound messages towards the peer and one for receiving inbound messages from the peer.

 CLUSTER LINKS outputs information of all such peer links as an array, where each array element is a map that contains attributes and their values for an individual link.

## Examples

The following is an example output:

[code example]

Each map is composed of the following attributes of the corresponding cluster link and their values:

1. direction : This link is established by the local node to the peer, or accepted by the local node from the peer.
2. node : The node id of the peer.
3. create-time : Creation time of the link. (In the case of a to link, this is the time when the TCP link is created by the local node, not the time when it is actually established.)
4. events : Events currently registered for the link. r means readable event, w means writable event.
5. send-buffer-allocated : Allocated size of the link's send buffer, which is used to buffer outgoing messages toward the peer.
6. send-buffer-used : Size of the portion of the link's send buffer that is currently holding data(messages).

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

Array reply: an array of maps where each map contains various attributes and their values of a cluster link.

-tab-sep-

Array reply: an array of Map reply where each map contains various attributes and their values of a cluster link.