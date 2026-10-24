The CLIENT LIST command returns information and statistics about the client
connections server in a mostly human readable format.

You can use one of the optional subcommands to filter the list. The TYPE type subcommand filters the list by clients' type, where *type* is one of normal , master , replica , and pubsub . Note that clients blocked by the MONITOR command belong to the normal class.

The ID filter only returns entries for clients with IDs matching the client-id arguments.

## Optional arguments

TYPE NORMAL | MASTER | REPLICA | PUBSUB

List only clients of the given type.

ID client-id [client-id ...]

List only the clients with the given IDs.

## Details

### Returned information

* id : a unique 64-bit client ID.
* addr : address/port of the client.
* laddr : address/port of local address client connected to (bind address).
* fd : file descriptor corresponding to the socket.
* name : the name set by the client with CLIENT SETNAME .
* age : total duration of the connection in seconds.
* idle : idle time of the connection in seconds.
* flags : client flags (see below).
* db : current database ID.
* sub : number of channel subscriptions.
* psub : number of pattern matching subscriptions.
* ssub : number of shard channel subscriptions. Added in Redis 7.0.3.
* multi : number of commands in a MULTI/EXEC context.
* watch : number of keys this client is currently watching. Added in Redis 7.4.
* qbuf : query buffer length (0 means no query pending).
* qbuf-free : free space of the query buffer (0 means the buffer is full).
* argv-mem : incomplete arguments for the next command (already extracted from query buffer).
* multi-mem : memory is used up by buffered multi commands. Added in Redis 7.0.
* obl : output buffer length.
* oll : output list length (replies are queued in this list when the buffer is full).
* omem : output buffer memory usage.
* tot-mem : total memory consumed by this client in its various buffers.
* events : file descriptor events (see below).
* cmd : last command played.
* user : the authenticated username of the client.
* redir : client id of current client tracking redirection.
* resp : client RESP protocol version. Added in Redis 7.0.
* rbp : peak size of the client's read buffer since the client connected. Added in Redis 7.0.
* rbs : current size of the client's read buffer in bytes. Added in Redis 7.0.
* lib-name - the name of the client library that is being used.
* lib-ver - the version of the client library.
* io-thread : id of I/O thread assigned to the client. Added in Redis 8.0.
* tot-net-in : total network input bytes read from this client.
* tot-net-out : total network output bytes sent to this client.
* tot-cmds : total count of commands this client executed.
* read-events : number of read events for this client. Added in Redis 8.8
* parse-batch-cmd-sum : cumulative number of commands parsed across all parsing batches for this client. Added in Redis 8.8
* parse-batch-cnt : total number of parsing batches for this client. Divide parse-batch-cmd-sum by this value to get the client’s average commands per batch. Added in Redis 8.8

The client flags can be a combination of:

[code example]

The file descriptor events can be:

[code example]

New fields are regularly added for debugging purpose. Some could be removed
in the future. A version safe Redis client using this command should parse
the output accordingly (i.e. handling gracefully missing fields, skipping
unknown fields).

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | |

## Return information

Bulk string reply: information and statistics about client connections.

-tab-sep-

Bulk string reply: information and statistics about client connections.