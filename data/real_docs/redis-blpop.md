> [!NOTE]
> This command's behavior varies in clustered Redis environments. See the multi-key operations page for more information.

 BLPOP is a blocking list pop primitive.
It is the blocking version of LPOP because it blocks the connection when there
are no elements to pop from any of the given lists.
An element is popped from the head of the first list that is non-empty, with the
given keys being checked in the order that they are given.

## Required arguments

key [key ...]

One or more keys of lists to operate on.

timeout

The maximum time to block, in seconds. A timeout of 0 blocks indefinitely.

## Examples

[code example]

## Details

### Non-blocking behavior

When BLPOP is called, if at least one of the specified keys contains a
non-empty list, an element is popped from the head of the list and returned to
the caller together with the key it was popped from.

Keys are checked in the order that they are given.
Let's say that the key list1 doesn't exist and list2 and list3 hold
non-empty lists.
Consider the following command:

[code example]

 BLPOP guarantees to return an element from the list stored at list2 (since
it is the first non empty list when checking list1 , list2 and list3 in
that order).

### Blocking behavior

If none of the specified keys exist, BLPOP blocks the connection until another
client performs an LPUSH or RPUSH operation against one of the keys.

Once new data is present on one of the lists, the client returns with the name
of the key unblocking it and the popped value.

When BLPOP causes a client to block and a non-zero timeout is specified,
the client will unblock returning a nil multi-bulk value when the specified
timeout has expired without a push operation against at least one of the
specified keys.

 The timeout argument is interpreted as a double value specifying the maximum number of seconds to block . A timeout of zero can be used to block indefinitely.

### What key is served first? What client? What element? Priority ordering details.

* If the client tries to block for multiple keys, but at least one key contains elements, the returned key/element pair is the first key from left to right that has one or more elements. In this case, the client is not blocked. For example, BLPOP key1 key2 key3 key4 0 , assuming that both key2 and key4 are non-empty, will always return an element from key2 .

* If multiple clients are blocked for the same key, the first client to be served is the one that has been waiting the longest (the first that blocked for the key). Once a client is unblocked it does not retain any priority; when it blocks again with another BLPOP call, it will be served according to its new position in the queue.

* When a client is blocking for multiple keys and multiple keys become non-empty as a result of the same command, transaction, or Lua script, the client is served according to the order of keys in its BLPOP call , not the order of the write operations. After the writes occur, Redis reprocesses the blocking command for the client and pops from the first non-empty key in the key list. 
For example, a client blocked on BLPOP key1 key2 0 will pop from key1 if both key1 and key2 receive elements during the same MULTI / EXEC transaction, because key1 appears first.

Internally, when a write makes progress possible for a blocked client, Redis marks that client as unblocked (adding it to an internal queue). No reply is sent immediately. Before the server goes idle (in the beforeSleep() phase), Redis rechecks the blocking command and serves the client based on the first non-empty key in its provided key list.

#### Example

 Client A 

[code example]

 Client B 

[code example]

Although key2 is pushed first inside the transaction, Redis reprocesses the blocking command for Client A after the transaction completes. 
At that time both lists are non-empty, and BLPOP pops from the first non-empty key in its argument list ( key1 ):

[code example]

To make Redis pop from key2 instead, reverse the order of the keys in the blocking call:

[code example]

### Behavior of BLPOP when multiple elements are pushed inside a list.

There are times when a list can receive multiple elements in the context of the same conceptual command:

* Variadic push operations such as LPUSH mylist a b c .
* After an EXEC of a MULTI block with multiple push operations against the same list.
* Executing a Lua Script with Redis 2.6 or newer.

When multiple elements are pushed inside a list where there are clients blocking, the behavior is different for Redis 2.4 and Redis 2.6 or newer.

For Redis 2.6 what happens is that the command performing multiple pushes is executed, and *only after* the execution of the command the blocked clients are served. Consider this sequence of commands.

 Client A: BLPOP foo 0
 Client B: LPUSH foo a b c

If the above condition happens using a Redis 2.6 server or greater, Client A will be served with the c element, because after the LPUSH command the list contains c,b,a , so taking an element from the left means to return c .

Instead Redis 2.4 works in a different way: clients are served *in the context* of the push operation, so as long as LPUSH foo a b c starts pushing the first element to the list, it will be delivered to the Client A , that will receive a (the first element pushed).

The behavior of Redis 2.4 creates a lot of problems when replicating or persisting data into the AOF file, so the much more generic and semantically simpler behavior was introduced into Redis 2.6 to prevent problems.

Note that for the same reason a Lua script or a MULTI/EXEC block may push elements into a list and afterward delete the list . In this case the blocked clients will not be served at all and will continue to be blocked as long as no data is present on the list after the execution of a single command, transaction, or script.

### BLPOP inside a MULTI / EXEC transaction

 BLPOP can be used with pipelining (sending multiple commands and
reading the replies in batch), however this setup makes sense almost solely
when it is the last command of the pipeline.

Using BLPOP inside a MULTI / EXEC block does not make a lot of sense
as it would require blocking the entire server in order to execute the block
atomically, which in turn does not allow other clients to perform a push
operation. For this reason the behavior of BLPOP inside MULTI / EXEC when the list is empty is to return a nil multi-bulk reply, which is the same
thing that happens when the timeout is reached.

If you like science fiction, think of time flowing at infinite speed inside a
 MULTI / EXEC block...

### Reliable queues

When BLPOP returns an element to the client, it also removes the element from the list. This means that the element only exists in the context of the client: if the client crashes while processing the returned element, it is lost forever.

This can be a problem with some application where we want a more reliable messaging system. When this is the case, please check the BRPOPLPUSH command, that is a variant of BLPOP that adds the returned element to a target list before returning it to the client.

### Pattern: event notification

Using blocking list operations it is possible to mount different blocking
primitives.
For instance for some application you may need to block waiting for elements
into a Redis Set, so that as far as a new element is added to the Set, it is
possible to retrieve it without resort to polling.
This would require a blocking version of SPOP that is not available, but using
blocking list operations we can easily accomplish this task.

The consumer will do:

[code example]

While in the producer side we'll use simply:

[code example]

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | |

## Return information

One of the following:
* Nil reply: no element could be popped and the timeout expired
* Array reply: the key from which the element was popped and the value of the popped element.

-tab-sep-

One of the following:
* Null reply: no element could be popped and the timeout expired
* Array reply: the key from which the element was popped and the value of the popped element.