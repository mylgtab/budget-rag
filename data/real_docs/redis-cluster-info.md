CLUSTER INFO provides INFO style information about Redis Cluster vital parameters.
The following fields are always present in the reply:

[code example]

* cluster_state : State is ok if the node is able to receive queries. fail if there is at least one hash slot which is unbound (no node associated), in error state (node serving it is flagged with FAIL flag), or if the majority of masters can't be reached by this node.
* cluster_slots_assigned : Number of slots which are associated to some node (not unbound). This number should be 16384 for the node to work properly, which means that each hash slot should be mapped to a node.
* cluster_slots_ok : Number of hash slots mapping to a node not in FAIL or PFAIL state.
* cluster_slots_pfail : Number of hash slots mapping to a node in PFAIL state. Note that those hash slots still work correctly, as long as the PFAIL state is not promoted to FAIL by the failure detection algorithm. PFAIL only means that we are currently not able to talk with the node, but may be just a transient error.
* cluster_slots_fail : Number of hash slots mapping to a node in FAIL state. If this number is not zero the node is not able to serve queries unless cluster-require-full-coverage is set to no in the configuration.
* cluster_known_nodes : The total number of known nodes in the cluster, including nodes in HANDSHAKE state that may not currently be proper members of the cluster.
* cluster_size : The number of master nodes serving at least one hash slot in the cluster.
* cluster_current_epoch : The local Current Epoch variable. This is used in order to create unique increasing version numbers during fail overs.
* cluster_my_epoch : The Config Epoch of the node we are talking with. This is the current configuration version assigned to this node.
* cluster_stats_messages_sent : Number of messages sent via the cluster node-to-node binary bus.
* cluster_stats_messages_received : Number of messages received via the cluster node-to-node binary bus.
* total_cluster_links_buffer_limit_exceeded : Accumulated count of cluster links freed due to exceeding the cluster-link-sendbuf-limit configuration.

The following atomic slot migration fields may be included in the reply (available since Redis 8.4.0):

* cluster_slot_migration_active_tasks : Number of in-progress ASM tasks. Currently, it will be 1 or 0.
* cluster_slot_migration_active_trim_running : Number of active trim jobs in progress and scheduled.
* cluster_slot_migration_active_trim_current_job_keys : Number of keys scheduled for deletion in the current trim job.
* cluster_slot_migration_active_trim_current_job_trimmed : Number of keys already deleted in the current trim job.
* cluster_slot_migration_stats_active_trim_started : Total number of trim jobs that have started since the process began.
* cluster_slot_migration_stats_active_trim_completed : Total number of trim jobs completed since the process began.
* cluster_slot_migration_stats_active_trim_cancelled : Total number of trim jobs cancelled since the process began.

The following message-related fields may be included in the reply if the value is not 0:
Each message type includes statistics on the number of messages sent and received.
Here are the explanation of these fields:

* cluster_stats_messages_ping_sent and cluster_stats_messages_ping_received : Cluster bus PING (not to be confused with the client command PING ).
* cluster_stats_messages_pong_sent and cluster_stats_messages_pong_received : PONG (reply to PING).
* cluster_stats_messages_meet_sent and cluster_stats_messages_meet_received : Handshake message sent to a new node, either through gossip or CLUSTER MEET .
* cluster_stats_messages_fail_sent and cluster_stats_messages_fail_received : Mark node xxx as failing.
* cluster_stats_messages_publish_sent and cluster_stats_messages_publish_received : Pub/Sub Publish propagation, see Pubsub.
* cluster_stats_messages_auth-req_sent and cluster_stats_messages_auth-req_received : Replica initiated leader election to replace its master.
* cluster_stats_messages_auth-ack_sent and cluster_stats_messages_auth-ack_received : Message indicating a vote during leader election.
* cluster_stats_messages_update_sent and cluster_stats_messages_update_received : Another node slots configuration.
* cluster_stats_messages_mfstart_sent and cluster_stats_messages_mfstart_received : Pause clients for manual failover.
* cluster_stats_messages_module_sent and cluster_stats_messages_module_received : Module cluster API message.
* cluster_stats_messages_publishshard_sent and cluster_stats_messages_publishshard_received : Pub/Sub Publish shard propagation, see Sharded Pubsub.

More information about the Current Epoch and Config Epoch variables are available in the Redis Cluster specification document.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | Only supported with the OSS cluster API. |

## Return information

Bulk string reply: A map between named fields and values in the form of : lines separated by newlines composed by the two bytes CRLF .

-tab-sep-

Bulk string reply: A map between named fields and values in the form of : lines separated by newlines composed by the two bytes CRLF