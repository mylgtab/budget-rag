> [!NOTE]
> Jedis 7.2.0 introduced a new client connection API:
>
> | New API class | Replaces | Use case |
> |:-- |:-- |:-- |
> | RedisClient | UnifiedJedis, JedisPool, JedisPooled | Single connection (with connection pooling) |
> | RedisClusterClient | JedisCluster | Redis Cluster connections |
> | RedisSentinelClient | JedisSentinelPool | Redis Sentinel connections |
>
> The old client classes are now considered deprecated.

## Basic connection

The following code opens a basic connection to a local Redis server:

[code example]

> [!NOTE]
> Jedis supports connection URLs through RedisClient.create().
> A URL can set the host, port, credentials, database, and whether to use TLS,
> so you can use one instead of passing those options separately.

After you have connected, you can check the connection by storing and
retrieving a simple string value:

[code example]

### Connect to a Redis cluster

To connect to a Redis cluster, use RedisClusterClient. 

[code example]

### Connect to Redis Sentinel

To connect through Redis Sentinel,
use RedisSentinelClient. Pass the name of the primary that the Sentinels monitor to
 masterName(), and the Sentinel addresses to sentinels(). The client asks the Sentinels
for the current primary and switches to the new one after a failover.

[code example]

The Sentinels and the data nodes have separate credentials. Pass a client configuration for
the primary to clientConfig(), and one for the Sentinels to sentinelClientConfig():

[code example]

 RedisSentinelClient always sends commands to the primary. It doesn't support reading
from replicas.

### Connect to your production Redis with TLS

When you deploy your application, use TLS and follow the Redis security guidelines.

Before connecting your application to the TLS-enabled Redis server, ensure that your certificates and private keys are in the correct format.

To convert user certificate and private key from the PEM format to pkcs12, use this command:

[code example]

Enter password to protect your pkcs12 file.

Convert the server (CA) certificate to the JKS format using the keytool shipped with JDK.

[code example]

Establish a secure connection with your Redis database using this snippet.

[code example]

## Connect using client-side caching

Client-side caching is a technique to reduce network traffic between
the client and server, resulting in better performance. See
Client-side caching introduction
for more information about how client-side caching works and how to use it effectively.

To enable client-side caching, specify the
RESP3
protocol and pass a cache configuration object during the connection.

The example below shows the simplest client-side caching connection to the default host and port,
 localhost:6379.
All of the connection variants described above accept these parameters, so you can
use client-side caching with a connection pool or a cluster connection in exactly the same way.

> [!NOTE]
> Client-side caching requires Jedis v5.2.0 or later.
> To maximize compatibility with all Redis products, client-side caching
> is supported by Redis v7.4 or later.
>
> The Redis server products support
> opt-in/opt-out mode
> and broadcasting mode
> for CSC, but these modes are not currently implemented by Jedis.

[code example]

Once you have connected, the usual Redis commands will work transparently
with the cache:

[code example]

You can see the cache working if you connect to the same Redis database
with redis-cli and run the
 MONITOR command. If you run the
code above but without passing cacheConfig during the connection,
you should see the following in the CLI among the output from MONITOR:

[code example]

The server responds to both get("city") calls.
If you run the code with cacheConfig added in again, you will see

[code example]

The first get("city") call contacted the server, but the second
call was satisfied by the cache.

### Removing items from the cache

You can remove individual keys from the cache with the
 deleteByRedisKey() method of the cache object. This removes all cached items associated
with each specified key, so all results from multi-key commands (such as
 MGET ) and composite data structures
(such as hashes) will be
cleared at once. The example below shows the effect of removing a single
key from the cache:

[code example]

You can also clear all cached items using the flush() 
method:

[code example]

The client will also flush the cache automatically
if any connection (including one from a connection pool)
is disconnected.

## Configure a connection pool

A connection pool maintains several open connections and reuses them
efficiently. When you open a connection from a pool, the pool allocates
one of its open connections. When you subsequently close the same connection,
it is not actually closed but simply returned to the pool for reuse.
This avoids the overhead of repeated connecting and disconnecting.
See
Connection pools and multiplexing
for more information.

From Jedis 7.2.0, the RedisClient class provides connection pooling automatically,
but it's important to configure the connection pool correctly to get the best performance. 
Each pool holds a specified number of connections, creates more connections when necessary, and terminates them when they are no longer needed.

Here is a simplified connection lifecycle in a pool:

1. A connection is requested from the pool.
2. A connection is served:
 - An idle connection is served when non-active connections are available, or 
 - A new connection is created when the number of connections is under maxTotal. 
3. The connection becomes active.
4. The connection is released back to the pool.
5. The connection is marked as stale. 
6. The connection is kept idle for minEvictableIdleTime. 
7. The connection becomes evictable if the number of connections is greater than minIdle. 
8. The connection is ready to be closed.

Pass a ConnectionPoolConfig object to the RedisClient builder to configure the pool. 
( ConnectionPoolConfig is a wrapper around GenericObjectPoolConfig from Apache Commons Pool2).

[code example]

### Retrying a command after a connection failure

If a connection is lost before a command is completed, the command will fail with a JedisConnectionException. Although the connection pool manages the connections
for you, you must request a new connection from the pool to retry the command.
You would typically do this in a loop that makes several attempts to reconnect
before aborting and reporting that the error isn't transient. The example below
shows a retry loop that uses a simple
exponential backoff
strategy:

[code example]