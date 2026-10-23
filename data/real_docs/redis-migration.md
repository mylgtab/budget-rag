Redis previously recommended the ioredis 
client library for development with Node.js,
but this library is now deprecated in favor of
 node-redis. This guide
outlines the main similarities and differences between the two libraries.
You may find this information useful if you are an ioredis user and you want to
start a new Node.js project or migrate an existing ioredis project to node-redis.

## Comparison of ioredis and node-redis 

The tables below summarize how ioredis and node-redis implement some
key features of Redis. See the following sections for more information about
each feature.

### Connection

| Feature | ioredis | node-redis |

| Initial connection | Happens when you create a client instance | Requires you to call a method on the client instance |
| Reconnection after a connection is lost | Automatic by default | Automatic by default and configurable |
| Connection events | Emits connect, ready, error, and close events | Emits connect, ready, error, end, and reconnecting events |

### Command handling

| Feature | ioredis | node-redis |

| Command case | Lowercase only (eg, hset ) | Uppercase or camel case (eg, HSET or hSet ) |
| Command argument handling | Argument objects flattened and items passed directly | Argument objects parsed to generate correct argument list |
| Asynchronous command result handling | Callbacks and Promises | Promises (but supports callbacks via Legacy Mode) |
| Arbitrary command execution | Uses the call() method | Uses the sendCommand() method |

### Techniques

| Feature | ioredis | node-redis |

| Pipelining | Automatic, or with pipeline() command | Automatic, or with multi() command |
| Scan iteration | Uses scanStream(), etc | Uses scanIterator(), etc |
| Subscribing to channels | Uses client.on('message',...) event | Uses subscribe(...) command |

### Specific commands

| Command | ioredis | node-redis |

| SETNX | Supported explicitly | Supported as an option for SET |
| HMSET | Supported explicitly | Supported with standard HSET functionality |
| CONFIG | Supported explicitly | Supported with separate configGet(), configSet(), etc |co

## Details

The sections below explain the points of comparison between ioredis and
 node-redis in more detail.

### Initial connection

 ioredis makes the connection to the Redis server when you create an instance
of the client object:

[code example]

 node-redis requires you to call the connect() method on the client object
to make the connection:

[code example]

### Reconnection after a connection is lost {#reconnection}

Both ioredis and node-redis automatically attempt to reconnect if the connection
was lost due to an error. node-redis also lets you add a custom reconnection strategy
when you create the client object. See
Reconnect after disconnection
for more information.

### Connection events

The connect, ready, error, and close events that ioredis emits
are equivalent to the connect, ready, error, and end events
in node-redis, but node-redis also emits a reconnecting event.
See Connection events
for more information.

### Command case

Command methods in ioredis are always lowercase. With node-redis, you can
use uppercase or camel case versions of the method names.

[code example]

### Command argument handling

 ioredis parses command arguments to strings and then passes them to
the server, in a similar way to redis-cli.

[code example]

Arrays passed as arguments are flattened into individual elements and
objects are flattened into sequential key-value pairs:

[code example]

 node-redis uses predefined formats for command arguments. These include specific
classes for command options that generally don't correspond to the syntax
of the CLI command. Internally, node-redis constructs the correct command using
the method arguments you pass:

[code example]

### Asynchronous command result handling {#async-result}

All commands for both ioredis and node-redis are executed
asynchronously. ioredis supports both callbacks and
 Promise 
return values to respond to command results:

[code example]

 node-redis supports only Promise objects for results, so
you must always use a then() handler or the
 await 
operator to receive them. However, you can still use callbacks with the legacy mode if you need them:

[code example]

### Arbitrary command execution

 ioredis lets you issue arbitrary commands in a similar format to
 redis-cli using the call() 
command:

[code example]

In node-redis, you can get the same effect outside a transaction using sendCommand():

[code example]

Within a transaction, use addCommand() to include arbitrary commands. Note that
you can freely mix addCommand() calls with standard commands in the same
transaction:

[code example]

### Pipelining

Both ioredis and node-redis will pipeline commands automatically if
they are executed in the same "tick" of the
event loop
(see
Execute a pipeline
for more information).

You can also create a pipeline with explicit commands in both clients.
With ioredis, you use the pipeline() command with a chain of
commands, ending with exec() to run the pipeline:

[code example]

For node-redis, the approach is similar, except that you call the multi() 
command to start the pipeline and execAsPipeline() to run it:

[code example]

### Scan iteration

 ioredis supports the scanStream() method to create a readable stream
from the set of keys returned by the SCAN 
command:

[code example]

You can also use the similar hscanStream(), sscanStream(), and
 zscanStream() to iterate over the items of a hash, set, or sorted set,
respectively.

 node-redis handles scan iteration using the scanIterator() method
(and the corresponding hscanIterator(), sscanIterator(), and
 zscanIterator() methods). These return a collection object for
each page scanned by the cursor (this can be helpful to improve
efficiency using MGET and
other multi-key commands):

[code example]

### Subscribing to channels

 ioredis reports incoming pub/sub messages with a message 
event on the client object (see
Publish/subscribe for more
information about messages):

[code example]

With node-redis, you use the subscribe() command to register the
message callback. Also, when you use a connection to subscribe, that
connection can't issue any other commands, so you must create a
dedicated connection for the subscription. Use the client.duplicate() 
method to create a new connection with the same settings as the original:

[code example]

### SETNX command

 ioredis implements the SETNX 
command with an explicit method:

[code example]

 node-redis provides a SETNX method but this command is deprecated. Use the NX option to the SET 
command to get the same functionality as SETNX:

[code example]

### HMSET command

The HMSET command has been deprecated
since Redis v4.0.0, but it is still supported by ioredis. With node-redis 
you should use the HSET command with
multiple key-value pairs. See the HSET 
command page for more information.

### CONFIG command

 ioredis supports a config() method to set or get server configuration
options:

[code example]

 node-redis doesn't have a config() method, but instead supports the
standard commands configSet(),
 configGet(),
 configResetStat(), and
 configRewrite:

[code example]