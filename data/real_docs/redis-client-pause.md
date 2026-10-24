CLIENT PAUSE is a connections control command able to suspend all the Redis clients for the specified amount of time (in milliseconds).

The command performs the following actions:

* It stops processing all the pending commands from normal and pub/sub clients for the given mode. However, interactions with replicas will continue normally. Note that clients are formally paused when they try to execute a command, so no work is taken on the server side for inactive clients.
* It returns OK to the caller as soon as possible so the CLIENT PAUSE command execution is not itself paused.
* When the specified amount of time has elapsed, all the clients are unblocked; this will trigger the processing of all the commands accumulated in the query buffer of every client during the pause.

## Required arguments

timeout

How long to pause clients, in milliseconds.

## Optional arguments

WRITE | ALL

 ALL : This is the default mode. All client commands are blocked.

 WRITE : Clients are only blocked if they attempt to execute a write command.

## Details

For the WRITE mode, some commands have special behavior:

* EVAL / EVALSHA : Will block client for all scripts.
* PUBLISH : Will block client.
* PFCOUNT : Will block client.
* WAIT : Acknowledgments will be delayed, so this command will appear blocked.

This command is useful as it makes able to switch clients from a Redis instance to another one in a controlled way. For example during an instance upgrade the system administrator could do the following:

* Pause the clients using CLIENT PAUSE .
* Wait a few seconds to make sure the replicas processed the latest replication stream from the master.
* Turn one of the replicas into a master.
* Reconfigure clients to connect with the new master.

Since Redis 6.2, the recommended mode for client pause is WRITE . This mode will stop all replication traffic, can be
aborted with the CLIENT UNPAUSE command, and allows reconfiguring the old master without risking accepting writes after the
failover. This is also the mode used during cluster failover.

For Redis versions earlier than 6.2, you can send CLIENT PAUSE in a MULTI/EXEC block with INFO replication to get the current master offset when Redis blocks clients. You can then wait for that offset on the replica to make sure the replica has processed the full replication stream.

Starting with Redis 3.2.10 and 4.0.0, this command also prevents keys from being evicted or expired while clients are paused. This keeps the dataset static during the pause: clients cannot write to it, and Redis does not change it through eviction or expiration.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

Simple string reply: OK or an error if the timeout is invalid.

-tab-sep-

Simple string reply: OK or an error if the timeout is invalid.